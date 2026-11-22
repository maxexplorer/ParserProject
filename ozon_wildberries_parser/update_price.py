# update_price.py

import time

import pandas as pd
import openpyxl

from excel_io import DATA_WORKBOOK, find_workbook, save_workbook

from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS
from api_requests import ApiError, read_json, send_request, wb_goods, wb_json


def load_article_info_from_excel(sheet_name: str) -> dict:
    """
    Загружает артикулы и new_price из Excel, начиная с 3 строки (skiprows=2).
    Артикул в 1 столбце, new_price в 6 столбце.
    Возвращает словарь {offer_id: delta}
    """
    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    df = pd.read_excel(source, sheet_name=sheet_name, skiprows=2)
    df.columns = df.columns.str.strip()

    article_info = {}
    for _, row in df.iterrows():
        article = str(row.iloc[1]).strip()
        if not article:
            continue

        new_price = row.iloc[6]  # 6 столбец

        if pd.isna(new_price) or new_price == '' or new_price == ' ':
            continue

        try:
            delta = float(new_price)
            article_info[article] = delta
        except Exception as ex:
            print(f'Ошибка преобразования для {article}: {ex}')
            continue

    return article_info


def get_current_prices_ozon() -> dict:
    """
    Получает текущие маркетинговые цены товаров с Ozon.
    :return: Словарь {offer_id: current_price}
    """
    result = {}
    cursor = ''
    seen = set()
    received = 0
    limit = 100

    while True:
        data = {
            'cursor': cursor,
            'filter': {
                'offer_id': [],
                'product_id': [],
                'visibility': 'IN_SALE'
            },
            'limit': limit
        }

        time.sleep(1)
        label = 'Ozon (цены)'
        response = send_request(
            'POST', API_URLS_OZON['product_info_prices'], label=label, headers=OZON_HEADERS,
            json=data, timeout=15,
        )
        data = read_json(response, label)
        items = data['items']
        if not isinstance(items, list):
            raise ApiError(f'{label}: некорректный список товаров.')
        received += len(items)
        total = data.get('total_items', data.get('total'))
        cursor = data.get('cursor', data.get('last_id', ''))
        if total is not None and total > received and (not cursor or not items):
            raise ApiError(f'{label}: пагинация завершилась до получения всех товаров.')

        for item in items:
            offer_id = item.get('offer_id')
            if offer_id:
                result[offer_id] = float(item['price']['price'])

        if not cursor or not items:
            break
        if cursor in seen:
            raise ApiError('Ozon (цены): повторный курсор.')
        seen.add(cursor)

    return result


def get_current_prices_wb() -> tuple[dict, dict]:
    vendor_code_to_price = {}
    vendor_code_to_nm_id = {}
    for item in wb_goods({'order': 'nmId', 'direction': 'asc'}):
        vendor_code = item['vendorCode']
        sizes = item['sizes']
        if sizes and vendor_code:
            vendor_code_to_price[vendor_code] = float(sizes[0]['price'])
            vendor_code_to_nm_id[vendor_code] = item['nmID']

    return vendor_code_to_price, vendor_code_to_nm_id


def update_prices_ozon(article_info: dict) -> dict:
    """
    Обновляет цены на Ozon по API и возвращает текущие цены для записи в Excel.
    """
    current_prices = get_current_prices_ozon()
    prices = {'prices': []}

    for offer_id, delta in article_info.items():
        current_price = current_prices.get(offer_id)
        if current_price is None:
            print(f'❗ Не найдена текущая цена для Ozon offer_id: {offer_id}')
            continue

        new_price = current_price + delta

        prices['prices'].append({
            'auto_action_enabled': 'UNKNOWN',
            'auto_add_to_ozon_actions_list_enabled': 'UNKNOWN',
            'currency_code': 'RUB',
            'min_price': str(int(new_price)),
            'min_price_for_auto_actions_enabled': True,
            'net_price': '0',
            'offer_id': offer_id,
            'old_price': '0',
            'price': str(int(new_price)),
            'price_strategy_enabled': 'UNKNOWN',
            'product_id': 0,
            'quant_size': 1,
            'vat': '0'
        })

    if prices['prices']:
        label = 'Ozon (обновление цен)'
        response = send_request(
            'POST', API_URLS_OZON['import_price'], label=label, headers=OZON_HEADERS, json=prices,
        )
        items = read_json(response, label)['result']
        if (not isinstance(items, list) or len(items) != len(prices['prices'])
                or any(item.get('updated') is not True or item.get('errors') for item in items)):
            raise ApiError(f'{label}: API не подтвердил обновление всех цен.')

    return current_prices


def update_prices_wb(article_info: dict) -> dict:
    """
    Обновляет цены на Ozon по API и возвращает текущие цены для записи в Excel.
    """
    vendor_code_to_price, vendor_code_to_nmID = get_current_prices_wb()
    data = {'data': []}

    for vendor_code, delta in article_info.items():
        current_price = vendor_code_to_price.get(vendor_code)
        nm_id = vendor_code_to_nmID.get(vendor_code)

        if current_price is None:
            print(f'❗ Не найдена текущая цена для WB vendorCode: {vendor_code}')
            continue
        if nm_id is None:
            print(f'❗ Не найден nmID для WB vendorCode: {vendor_code}')
            continue

        new_price = current_price + delta

        data['data'].append({
            'nmID': int(nm_id),
            'price': int(new_price),
            'discount': 0
        })

    if data['data']:
        result = wb_json('POST', API_URLS_WB['upload_task'], 'prices',
                         json=data, statuses=(200, 208), retry=False)
        if result.get('error') or not isinstance(result.get('data'), dict):
            raise ApiError('Wildberries: API не подтвердил приём задачи обновления цен.')

    return vendor_code_to_price


def write_price_to_excel(current_prices: dict, marketplace='ОЗОН') -> None:
    """
    Обновляет цены в 5-м столбце (индекс 4) Excel для указанного листа marketplace,
    сохраняя изменения в data/data.xlsx.
    """
    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return

    wb = openpyxl.load_workbook(source)
    if marketplace not in wb.sheetnames:
        print(f'❗ В книге нет листа "{marketplace}"')
        return

    ws = wb[marketplace]

    for row in ws.iter_rows(min_row=4):
        cell_article = row[1].value
        if not cell_article:
            continue
        offer_id = str(cell_article).strip()
        price_value = current_prices.get(offer_id)
        if price_value is not None:
            ws.cell(row=row[1].row, column=6, value=price_value)

    save_workbook(wb)
    print(f'✅ Текущие цены успешно записаны в {DATA_WORKBOOK}')
