# analytics_report.py

import os
import time
import glob
from datetime import datetime, timedelta

import requests
import openpyxl

from configs.config import API_URLS_OZON, OZON_HEADERS, API_URLS_WB, WB_ANALYTICS_HEADERS


def get_all_products() -> dict:
    """
    Получает соответствие {product_id: offer_id} для всех товаров Ozon.
    Используется для сопоставления id из отчёта аналитики с артикулами.
    """
    all_products = {}
    last_id = ''
    limit = 100

    while True:
        payload = {
            'filter': {
                'visibility': 'IN_SALE'
            },
            'last_id': last_id,
            'limit': limit
        }

        try:
            response = requests.post(
                API_URLS_OZON['product_list'],
                headers=OZON_HEADERS,
                json=payload,
                timeout=20
            )
            response.raise_for_status()
        except Exception as ex:
            print(f'❌ Ошибка при получении товаров Ozon: {ex}')
            break

        data = response.json()
        result = data.get('result', {})
        items = result.get('items', [])
        total = result.get('total')

        print(f'📦 Всего товаров: {total} | Загружено: {len(all_products)}')

        for item in items:
            product_id = str(item.get('product_id'))
            offer_id = str(item.get('offer_id'))
            if product_id and offer_id:
                all_products[product_id] = offer_id

        # Переходим к следующей странице
        last_id = result.get('last_id', '')
        if not last_id:
            break

    print(f'✅ Загружено {len(all_products)} товаров Ozon')
    return all_products


def get_ozon_orders_report(period: str) -> dict:
    """
    Получение количества заказов по offer_id за месяц или неделю.
    """
    now = datetime.now()
    if period == 'month':
        date_from = (now - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period == 'week':
        date_from = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        raise ValueError('period должен быть "month" или "week"')
    date_to = now.strftime('%Y-%m-%d')

    data = {
        'date_from': date_from,
        'date_to': date_to,
        'metrics': ['ordered_units'],
        'dimension': ['sku', period],
        'filters': [],
        'limit': 1000,
        'offset': 0
    }

    orders = {}
    while True:
        try:
            response = requests.post(
                API_URLS_OZON['analytics_data'],
                headers=OZON_HEADERS,
                json=data,
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            for item in data['result']['data']:
                offer_id = item['dimensions'][0]['id']
                ordered_units = int(item['metrics'][0])
                orders[offer_id] = orders.get(offer_id, 0) + ordered_units
            if len(data['result']['data']) < data['limit']:
                break
            data['offset'] += data['limit']
        except Exception as ex:
            print(f'❌ Ошибка получения данных OZON: {ex}')
            break
    return orders


def get_wb_orders_report(period: str) -> dict:
    """
    Получение количества заказов по vendorCode за месяц или неделю.
    """
    now = datetime.now()
    if period == 'month':
        date_from = (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    elif period == 'week':
        date_from = (now - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise ValueError('period должен быть "month" или "week"')
    date_to = now.strftime('%Y-%m-%d %H:%M:%S')

    page = 1
    orders = {}
    while True:
        data = {
            "brandNames": [],
            "objectIDs": [],
            "tagIDs": [],
            "nmIDs": [],
            "timezone": "Europe/Moscow",
            "period": {
                "begin": date_from,
                "end": date_to
            },
            "orderBy": {
                "field": "ordersSumRub",
                "mode": "asc"
            },
            "page": page
        }
        try:
            response = requests.post(
                API_URLS_WB['report_detail'],
                headers=WB_ANALYTICS_HEADERS,
                json=data,
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            for card in data['data']['cards']:
                vendor_code = card['vendorCode']
                orders_count = card['statistics']['selectedPeriod']['ordersCount']
                orders[vendor_code] = orders.get(vendor_code, 0) + orders_count
            if not data['data']['isNextPage']:
                break
            page += 1
        except Exception as ex:
            print(f'❌ Ошибка получения данных WB: {ex}')
            break
    return orders


def write_analytics_to_excel(
        analytics_data: dict,
        marketplace='ОЗОН',
        column_month=11,
        column_week=12,
        period='month'
) -> None:
    """
    Записывает данные аналитики (кол-во заказов) в Excel в указанный столбец по period.

    analytics_data: {offer_id: orders_count}
    period: 'month' или 'week' для определения в какую колонку писать
    """
    folder = 'data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return

    wb = openpyxl.load_workbook(excel_files[0])
    if marketplace not in wb.sheetnames:
        print(f'❗ В книге нет листа "{marketplace}"')
        return

    ws = wb[marketplace]
    target_column = column_month if period == 'month' else column_week

    for row in ws.iter_rows(min_row=4):
        cell_article = row[0].value
        if not cell_article:
            continue
        offer_id = str(cell_article).strip()
        if offer_id in analytics_data:
            orders_count = analytics_data[offer_id]
            row[target_column - 1].value = orders_count

    if not os.path.exists(folder):
        os.makedirs(folder)

    output_path = os.path.join(folder, 'data.xlsx')
    wb.save(output_path)
    print(f'✅ Данные аналитики успешно записаны в {output_path}')
