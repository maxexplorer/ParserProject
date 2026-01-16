# upload_images.py

import os
import glob
import time

import requests
import pandas as pd


from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS, WB_CONTENT_HEADERS
from configs.config import FIGMA_HEADERS

def load_image_tasks_from_excel() -> list[dict]:
    folder = 'data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ Нет Excel файлов')
        return []

    df = pd.read_excel(excel_files[1])
    df.columns = df.columns.str.strip()

    tasks = []

    for _, row in df.iterrows():
        wb_flag = str(row.iloc[0]).strip().lower()
        ozon_flag = str(row.iloc[1]).strip().lower()

        product_id_ozon = row.iloc[3]
        nm_id_wb = row.iloc[4]
        figma_key = str(row.iloc[5]).strip()

        if not figma_key:
            continue

        node_ids = []
        for col in range(6, 16):  # G → P
            val = row.iloc[col]
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


def get_figma_image_urls(figma_key: str, node_ids: list[str]) -> list[str]:
    url = f'https://api.figma.com/v1/images/{figma_key}'

    params = {
        'ids': ','.join(node_ids),
        'format': 'jpg',
        'scale': 2
    }

    time.sleep(3)
    response = requests.get(url, headers=FIGMA_HEADERS, params=params)
    # response.raise_for_status()

    data = response.json()
    images = data.get('images', {})

    return [img_url for img_url in images.values() if img_url]



def upload_images_ozon(product_id: int, image_urls: list[str]):
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

    print(response.text)

    response.raise_for_status()
    return response.json()


def upload_images_wb(nm_id: int, image_urls: list[str]):
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

def process_image_uploads():
    tasks = load_image_tasks_from_excel()

    for task in tasks:
        print(f"🔹 Обработка Figma {task['figma_key']}")

        image_urls = get_figma_image_urls(
            figma_key=task['figma_key'],
            node_ids=task['node_ids']
        )

        # image_urls = [
        #     "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/c4ae8f88-d8fb-4b0f-9c2f-53f115b382e4",
        #     "https://figma-alpha-api.s3.us-west-2.amazonaws.com/images/3ca23ad5-dcbd-4bf9-bd67-8e5a1e29a7fe"
        # ]

        if task['ozon'] and task['product_id_ozon']:
            upload_images_ozon(task['product_id_ozon'], image_urls)
            print('✅ OZON обновлён')

        if task['wb'] and task['nm_id_wb']:
            upload_images_wb(task['nm_id_wb'], image_urls)
            print('✅ WB обновлён')


