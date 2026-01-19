# upload_images.py

import os
import glob
import time

import requests
import pandas as pd

from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS, WB_CONTENT_HEADERS
from configs.config import FIGMA_HEADERS

def load_image_tasks_from_excel() -> list:
    """
    Загружает задачи для обновления изображений из Excel-файлов в папке `data/`.

    Каждая задача содержит информацию:
    - Нужно ли обновлять OZON
    - Нужно ли обновлять WB
    - product_id OZON
    - nmId WB
    - ключ Figma файла
    - список node_id для экспорта изображений

    Возвращает:
        tasks (list of dict): список задач для обработки
    """
    folder = 'figma_data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ Нет Excel файлов')
        return []

    # Берем второй файл в папке, если их несколько
    df = pd.read_excel(excel_files[0])
    df.columns = df.columns.str.strip()  # убираем пробелы в названиях колонок

    tasks = []

    for _, row in df.iterrows():
        wb_flag = str(row.iloc[0]).strip().lower()
        ozon_flag = str(row.iloc[1]).strip().lower()

        product_id_ozon = row.iloc[3]
        nm_id_wb = row.iloc[4]
        figma_key = str(row.iloc[5]).strip()

        if not figma_key:
            continue

        # Считываем node_id для изображений из колонок G → P (6 → 15 индекс)
        node_ids = []

        for val in row.iloc[6:]:
            if pd.notna(val):
                node_ids.append(str(val).replace('-', ':'))

        if not node_ids:
            continue

        tasks.append({
            'ozon': ozon_flag == 'обновить',
            'wb': wb_flag == 'обновить',
            'product_id_ozon': int(product_id_ozon) if not pd.isna(product_id_ozon) else None,
            'nm_id_wb': int(nm_id_wb) if not pd.isna(nm_id_wb) else None,
            'figma_key': figma_key,
            'node_ids': node_ids
        })

    return tasks


def get_figma_image_urls(figma_key: str, node_ids: list) -> list:
    """
    Получает ссылки на экспортированные изображения из Figma по ключу файла и node_ids.

    Параметры:
        figma_key (str): ключ Figma файла (из URL)
        node_ids (list of str): список node_id слоев для экспорта

    Возвращает:
        image_urls (list of str): список URL изображений в формате JPG
    """
    url = f'https://api.figma.com/v1/images/{figma_key}'

    params = {
        'ids': ','.join(node_ids),  # node_id через запятую
        'format': 'jpg',
        'scale': 2  # увеличение для HD качества
    }

    # Небольшая пауза, чтобы снизить риск превышения лимита Figma
    time.sleep(3)

    response = requests.get(url, headers=FIGMA_HEADERS, params=params)
    response.raise_for_status()  # Можно раскомментировать для дебага

    data = response.json()
    images = data.get('images', {})

    # Возвращаем только существующие URL
    return [img_url for img_url in images.values() if img_url]


def upload_images_ozon(product_id: int, image_urls: list) -> dict | None:
    try:
        payload = {
            'product_id': product_id,
            'images': image_urls,
        }
        response = requests.post(
            API_URLS_OZON['product_pictures_import'],
            headers=OZON_HEADERS,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
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
        response = requests.post(
            API_URLS_WB['content_media'],
            headers=WB_CONTENT_HEADERS,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка загрузки на WB для nmId={nm_id}: {e}")
        return None


def process_image_uploads():
    """
    Основная функция обработки всех задач.

    1. Загружает задачи из Excel
    2. Получает URL изображений из Figma
    3. Загружает изображения на OZON и WB (если отмечено)
    """
    tasks = load_image_tasks_from_excel()

    for task in tasks:
        print(f"🔹 Обработка Figma {task['figma_key']}")

        image_urls = get_figma_image_urls(
            figma_key=task['figma_key'],
            node_ids=task['node_ids']
        )

        if task['ozon'] and task['product_id_ozon']:
            result = upload_images_ozon(task['product_id_ozon'], image_urls)
            if result is not None:
                print(f'✅ OZON обновлён для product_id={task["product_id_ozon"]}')

        if task['wb'] and task['nm_id_wb']:
            result = upload_images_wb(task['nm_id_wb'], image_urls)
            if result is not None:
                print(f'✅ WB обновлён для nmId={task["nm_id_wb"]}')



