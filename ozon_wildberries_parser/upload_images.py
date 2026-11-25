# upload_images.py

import os
import glob
import time
import re

import requests
import pandas as pd

from configs.config import API_URLS_OZON, API_URLS_WB
from figma_utils import get_figma_nodes
from utils import check_token, request_api

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
        print('❗ Нет Excel файлов')
        return []

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
    response = request_api('figma', requests.get, url, params=params, timeout=15)
    data = response.json()
    images = data.get('images', {})
    return [img_url for img_url in images.values() if img_url]


def upload_images_ozon(product_id: int, image_urls: list) -> dict | None:
    try:
        payload = {
            'product_id': product_id,
            'images': image_urls,
        }
        response = request_api(
            'ozon', requests.post,
            API_URLS_OZON['product_pictures_import'],
            json=payload,
            timeout=15
        )
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка загрузки на OZON для product_id={product_id}: {e}")
        return None


def upload_images_wb(nm_id: int, image_urls: list) -> dict | None:
    try:
        payload = {
            'nmId': nm_id,
            'data': image_urls
        }
        response = request_api(
            'wb', requests.post,
            API_URLS_WB['content_media'],
            json=payload,
            timeout=15
        )
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка загрузки на WB для nmId={nm_id}: {e}")
        return None


def process_image_uploads() -> bool:
    """
    Основная функция обработки всех задач.
    """
    tasks = load_image_tasks_from_excel()
    if not tasks:
        return True
    ozon_ready = any(task['ozon'] and task['product_id_ozon'] for task in tasks) and check_token('ozon')
    wb_ready = any(task['wb'] and task['nm_id_wb'] for task in tasks) and check_token('wb')
    if not (ozon_ready or wb_ready) or not check_token('figma'):
        return False

    figma_cache = {}  # кеш слоев по ключу

    for task in tasks:
        upload_ozon = ozon_ready and task['ozon'] and task['product_id_ozon']
        upload_wb = wb_ready and task['wb'] and task['nm_id_wb']
        if not (upload_ozon or upload_wb):
            continue
        print(f"🔹 Обработка Figma {task['figma_key']}")

        # --- Figma cache
        if task['figma_key'] not in figma_cache:
            figma_cache[task['figma_key']] = get_figma_nodes(task['figma_key'])

        node_mapping = figma_cache[task['figma_key']]

        # Преобразуем layer_names в node_ids
        node_ids = [node_mapping[name] for name in task['layer_names'] if name in node_mapping]

        image_urls = get_figma_image_urls(
            figma_key=task['figma_key'],
            node_ids=node_ids
        )

        # Добавляем видео ссылку в конец списка
        if task['video_url_wb']:
            image_urls.append(task['video_url_wb'])

        if upload_ozon:
            result = upload_images_ozon(task['product_id_ozon'], image_urls)
            if result:
                print(f'✅ OZON обновлён для product_id={task["product_id_ozon"]}')

        if upload_wb:
            result = upload_images_wb(task['nm_id_wb'], image_urls)
            if result:
                print(f'✅ WB обновлён для nmId={task["nm_id_wb"]}')

    return True
