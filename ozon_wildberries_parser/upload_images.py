# upload_images.py

import os
import glob
import time
import re

import requests
import pandas as pd

from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS
from configs.config import FIGMA_HEADERS
from api_requests import ApiError, read_json, send_request, wb_json
from figma_utils import get_figma_nodes

def gdrive_direct_link(url: str) -> str | None:
    """
    Преобразует ссылку Google Drive вида
    https://drive.google.com/file/d/FILE_ID/view?...
    в прямую ссылку для скачивания.
    """
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    else:
        return None

def load_image_tasks_from_excel() -> list:
    """
    Загружает задачи для обновления изображений из Excel-файлов.
    """
    folder = 'figma_data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        raise FileNotFoundError('В папке figma_data нет Excel-файла с задачами.')

    df = pd.read_excel(excel_files[0])
    df.columns = df.columns.str.strip()  # убираем пробелы в названиях колонок

    tasks = []

    for _, row in df.iterrows():
        wb_flag = str(row.iloc[0]).strip().lower()
        ozon_flag = str(row.iloc[1]).strip().lower()

        product_id_ozon = row.iloc[3]
        nm_id_wb = row.iloc[4]
        figma_key = str(row.iloc[5]).strip()

        video_url_wb = str(row.iloc[6]).strip()
        video_url_wb = gdrive_direct_link(video_url_wb) if video_url_wb else None

        if not figma_key:
            continue

        layer_names = []
        for val in row.iloc[7:]:
            if pd.notna(val):
                name = ''.join(str(val).split())
                if name:  # только непустые строки
                    layer_names.append(name)

        if not layer_names and not video_url_wb:
            continue

        tasks.append({
            'ozon': ozon_flag == 'обновить',
            'wb': wb_flag == 'обновить',
            'product_id_ozon': int(product_id_ozon) if not pd.isna(product_id_ozon) else None,
            'nm_id_wb': int(nm_id_wb) if not pd.isna(nm_id_wb) else None,
            'figma_key': figma_key,
            'video_url_wb': video_url_wb,
            'layer_names': layer_names
        })

    return tasks


def get_figma_image_urls(figma_key: str, node_ids: list) -> list:
    """
    Получает ссылки на экспортированные изображения из Figma по ключу файла и node_ids.
    """
    url = f'https://api.figma.com/v1/images/{figma_key}'
    params = {
        'ids': ','.join(node_ids),
        'format': 'jpg',
        'scale': 2
    }
    time.sleep(3)  # пауза для лимитов Figma
    response = requests.get(url, headers=FIGMA_HEADERS, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    images = data.get('images', {})
    return [img_url for img_url in images.values() if img_url]


def upload_images_ozon(product_id: int, image_urls: list) -> dict:
    label = 'Ozon (изображения)'
    response = send_request(
        'POST', API_URLS_OZON['product_pictures_import'], label=label,
        headers=OZON_HEADERS, json={'product_id': product_id, 'images': image_urls}, timeout=15,
    )
    result = read_json(response, label)
    if not isinstance(result, dict) or not result:
        raise ApiError(f'{label}: API не подтвердил приём запроса.')
    return result


def upload_images_wb(nm_id: int, image_urls: list) -> dict:
    if not image_urls:
        raise ApiError('Wildberries (изображения): нет ссылок для загрузки.')
    result = wb_json(
        'POST', API_URLS_WB['content_media'], 'media',
        json={'nmId': nm_id, 'data': image_urls}, timeout=15, retry=False,
    )
    if not isinstance(result, dict) or result.get('error') is not False:
        raise ApiError('Wildberries (изображения): API не подтвердил приём запроса.')
    return result


def process_image_uploads():
    """Обрабатывает задачи по каждой площадке и сообщает итог по запросам."""
    tasks = load_image_tasks_from_excel()
    figma_cache = {}
    accepted = failed = 0

    for number, task in enumerate(tasks, start=1):
        targets = [
            (label, task[id_field], upload) for flag, label, id_field, upload in (
                ('ozon', 'Ozon', 'product_id_ozon', upload_images_ozon),
                ('wb', 'Wildberries', 'nm_id_wb', upload_images_wb),
            ) if task[flag]
        ]
        if not targets:
            continue
        try:
            figma_key = task['figma_key']
            if figma_key not in figma_cache:
                figma_cache[figma_key] = get_figma_nodes(figma_key)
            node_mapping = figma_cache[figma_key]
            node_ids = [node_mapping[name] for name in task['layer_names'] if name in node_mapping]
            image_urls = get_figma_image_urls(figma_key=figma_key, node_ids=node_ids)
            missing_layers = len(task['layer_names']) - len(node_ids)
            missing_exports = len(set(node_ids)) - len(image_urls)
            if task['wb'] and (missing_layers or missing_exports > 0):
                print(f'⚠️ Задача №{number} (Wildberries): не найдены слои — {missing_layers}, '
                      f'нет ссылок экспорта — {max(0, missing_exports)}.')

            if task['video_url_wb']:
                image_urls.append(task['video_url_wb'])
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError):
            failed += len(targets)
            print(f'❌ Задача №{number}: не удалось получить изображения из Figma.')
            continue

        for label, product_id, upload in targets:
            try:
                if not product_id:
                    raise ApiError('В задаче отсутствует идентификатор товара.')
                upload(product_id, image_urls)
            except ApiError as error:
                failed += 1
                print(f'❌ Задача №{number} ({label}): {error}')
            else:
                accepted += 1

    print(f'Загрузка медиа: принято API — {accepted}, не подтверждено — {failed}.')
    if accepted:
        print('Появление файлов на карточках проверяется отдельно.')
