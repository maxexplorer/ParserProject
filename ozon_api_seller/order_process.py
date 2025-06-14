# order_process.py

import os
import time
from datetime import datetime, timedelta
import glob

import requests
import pandas as pd

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_excel


def get_cutoff_range(days: int = 7) -> tuple[str, str]:
    """
    Возвращает временной диапазон (от, до) в ISO формате за последние `days` дней.
    """
    cutoff_to = datetime.utcnow()
    cutoff_from = cutoff_to - timedelta(days=days)
    return cutoff_from.isoformat() + 'Z', cutoff_to.isoformat() + 'Z'


def fetch_orders(cutoff_from: str, cutoff_to: str) -> dict | None:
    """
    Выполняет POST-запрос к API Ozon для получения заказов со статусом "awaiting_packaging".
    """
    headers = {
        'Client-Id': CLIENT_ID,
        'Api-Key': API_KEY
    }

    json = {
        'dir': 'ASC',
        'filter': {
            'cutoff_from': cutoff_from,
            'cutoff_to': cutoff_to,
            'status': 'awaiting_packaging'
        },
        'limit': 100,
        'offset': 0,
        'with': {
            'analytics_data': True,
            'barcodes': True,
            'financial_data': True,
            'translit': True
        }
    }

    try:
        time.sleep(1)  # Пауза между запросами по требованиям API
        response = requests.post(API_URLS.get('unfulfilled_list'), headers=headers, json=json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'❌ Ошибка HTTP: {err}')
    except Exception as e:
        print(f'❌ Общая ошибка: {e}')
    return None


def load_info_from_excel(folder: str = 'data') -> dict:
    """
    Загружает артикулы и цены из первого найденного Excel-файла в папке `folder`.
    Возвращает словарь вида {артикул: цена}.
    """
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    path = excel_files[0]
    print(f'📄 Загружаю Excel: {path}')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Артикул', df.columns[2]])

    return {
        str(row['Артикул']).strip(): row.iloc[2]
        for _, row in df.iterrows()
    }


def extract_data(postings: list, article_prices: dict) -> list[dict]:
    """
    Извлекает данные из списка заказов и агрегирует одинаковые товары:
    если у товаров совпадают артикул, название и цена — их количество суммируется.
    """
    grouped = {}

    for post in postings:
        product = post.get('products', [{}])[0]
        offer_id = str(product.get('offer_id', '')).strip()

        if offer_id not in article_prices:
            continue  # Пропускаем товары без известной цены

        name = product.get('name', '').strip()
        quantity = int(product.get('quantity', 0))
        price = article_prices[offer_id]

        key = (offer_id, name, price)  # Уникальный ключ для группировки

        if key in grouped:
            grouped[key] += quantity
        else:
            grouped[key] = quantity

    # Преобразуем в список словарей
    return [
        {
            'Артикул': k[0],
            'Наименование': k[1],
            'Цена': k[2],
            'Количество': v
        }
        for k, v in grouped.items()
    ]

def run_order_process():
    """
    Главная функция:
    - Получает заказы с Ozon
    - Загружает цены из Excel
    - Извлекает и агрегирует данные
    - Сохраняет в Excel
    """
    print('📦 Получение заказов с Ozon...')
    cutoff_from, cutoff_to = get_cutoff_range(7)
    print(f'⏱ Период: {cutoff_from} → {cutoff_to}')

    orders = fetch_orders(cutoff_from, cutoff_to)
    if not orders:
        return

    postings = orders.get('result', {}).get('postings', [])
    if not postings:
        print('❗ Заказов со статусом "awaiting_packaging" не найдено.')
        return

    article_info = load_info_from_excel()
    result = extract_data(postings, article_info)
    if not result:
        print('❗ Нет подходящих товаров для сохранения.')
        return

    save_excel(data=result, filename_prefix='results/ozon_orders')
