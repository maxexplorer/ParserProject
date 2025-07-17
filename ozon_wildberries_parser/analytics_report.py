# analytics_report.py

import requests
from datetime import datetime, timedelta
import openpyxl
import os

from configs.config import API_URLS_OZON, OZON_HEADERS, API_URLS_WB, WB_HEADERS

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
        "date_from": date_from,
        "date_to": date_to,
        "metrics": ["ordered_units"],
        "dimension": ["sku", "week" if period == 'week' else "sku", "month"],
        "filters": [],
        "limit": 1000,
        "offset": 0
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
                headers=WB_HEADERS,
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


def write_orders_to_excel(ozon_orders: dict, wb_orders: dict, period: str):
    """
    Запись количества заказов:
    - в 11 столбец для месяца
    - в 12 столбец для недели
    """
    path = 'data/data.xlsx'
    if not os.path.exists(path):
        print(f'❌ Файл {path} не найден.')
        return

    wb = openpyxl.load_workbook(path)

    def update_sheet(sheet_name, orders_dict, col_idx):
        if sheet_name not in wb.sheetnames:
            print(f'❌ Лист {sheet_name} не найден в файле.')
            return
        ws = wb[sheet_name]
        for row in ws.iter_rows(min_row=4):
            article = str(row[0].value).strip() if row[0].value else None
            if article and article in orders_dict:
                row[col_idx - 1].value = orders_dict[article]

    if ozon_orders:
        update_sheet('ОЗОН', ozon_orders, 11 if period == 'month' else 12)
    if wb_orders:
        update_sheet('ВБ', wb_orders, 11 if period == 'month' else 12)

    wb.save(path)
    print(f'✅ Отчет записан в {path}')

