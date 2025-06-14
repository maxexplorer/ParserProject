# process_orders.py

import os
import time
from datetime import datetime, timedelta
import glob

import requests
import pandas as pd

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_excel


def get_cutoff_range(days=7):
    """
    Возвращает временной диапазон в ISO-формате за последние `days` дней.

    :param days: Количество дней назад от текущего времени
    :return: Кортеж строк (от, до)
    """
    cutoff_to = datetime.utcnow()
    cutoff_from = cutoff_to - timedelta(days=days)
    return cutoff_from.isoformat() + 'Z', cutoff_to.isoformat() + 'Z'


def fetch_orders(cutoff_from, cutoff_to):
    """
    Получает список заказов со статусом "awaiting_packaging" из Ozon API.

    :param cutoff_from: Начало временного диапазона
    :param cutoff_to: Конец временного диапазона
    :return: JSON-ответ от API в виде словаря или None в случае ошибки
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
        time.sleep(1)  # Пауза между запросами для соблюдения лимитов
        response = requests.post(API_URLS.get('unfulfilled_list'), headers=headers, json=json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'❌ Ошибка HTTP: {err}')
    except Exception as e:
        print(f'❌ Общая ошибка: {e}')
    return None


def load_info_from_excel(folder='data'):
    """
    Загружает артикулы и цены из первого Excel-файла в указанной папке.

    :param folder: Папка, в которой искать Excel-файл
    :return: Словарь вида {артикул: цена}
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

    article_prices = {}
    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        price = row.iloc[2]
        article_prices[article] = price

    return article_prices


def extract_data(postings, article_prices):
    """
    Агрегирует товары из заказов по артикулу, названию и цене.

    :param postings: Список заказов от API
    :param article_prices: Словарь артикулов с ценами
    :return: Список словарей с полями Артикул, Наименование, Цена, Количество
    """
    grouped = {}

    for post in postings:
        product = post.get('products', [{}])[0]
        offer_id = str(product.get('offer_id', '')).strip()

        if offer_id not in article_prices:
            continue  # Пропускаем, если артикул не найден в Excel

        name = product.get('name', '').strip()
        quantity = int(product.get('quantity', 0))
        price = article_prices[offer_id]

        key = (offer_id, name, price)
        if key in grouped:
            grouped[key] += quantity
        else:
            grouped[key] = quantity

    result = []
    for key, qty in grouped.items():
        offer_id, name, price = key
        result.append({
            'Артикул': offer_id,
            'Наименование': name,
            'Цена': price,
            'Количество': qty
        })

    return result


def run_order_process():
    """
    Главная функция:
    - Получает заказы с Ozon
    - Загружает артикулы и цены из Excel
    - Агрегирует данные
    - Сохраняет результат в Excel
    """
    print('📦 Получение заказов с Ozon...')
    cutoff_from, cutoff_to = get_cutoff_range(7)
    print(f'⏱ Период: {cutoff_from} → {cutoff_to}')

    orders = fetch_orders(cutoff_from, cutoff_to)
    if not orders:
        print('❗ Не удалось получить список заказов.')
        return

    postings = orders.get('result', {}).get('postings', [])
    if not postings:
        print('❗ Заказов со статусом "awaiting_packaging" не найдено.')
        return

    article_info = load_info_from_excel()
    if not article_info:
        print('❗ Не удалось загрузить данные из Excel.')
        return

    result = extract_data(postings, article_info)
    if not result:
        print('❗ Нет подходящих товаров для сохранения.')
        return

    save_excel(data=result, filename_prefix='results/ozon_orders')
