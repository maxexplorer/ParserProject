# update_price.py

import math
import time
from collections import Counter

import pandas as pd
from openpyxl import load_workbook

from excel_io import DATA_WORKBOOK, find_workbook, save_workbook

from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS
from api_requests import ApiError, read_json, send_request, wb_goods, wb_json


def load_article_info_from_excel(sheet_name: str, *, path=DATA_WORKBOOK) -> dict:
    """Читает артикул из столбца B и изменение цены из столбца G."""
    source = find_workbook(path)
    df = pd.read_excel(source, sheet_name=sheet_name, skiprows=2)
    df.columns = df.columns.str.strip()

    article_info = {}
    invalid_rows = 0
    for _, row in df.iterrows():
        new_price = row.iloc[6]
        if pd.isna(new_price) or (isinstance(new_price, str) and not new_price.strip()):
            continue

        article = row.iloc[1]
        try:
            delta = float(new_price)
            if pd.isna(article) or not str(article).strip() or not math.isfinite(delta):
                raise ValueError
        except (ValueError, TypeError, OverflowError):
            invalid_rows += 1
            continue
        article_info[str(article).strip()] = delta

    if invalid_rows:
        print(f'Excel ({sheet_name}): пропущено некорректных строк с изменением цены — {invalid_rows}.')
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
        try:
            vendor_code = item['vendorCode']
            sizes = item['sizes']
            if not isinstance(vendor_code, str) or not isinstance(sizes, list):
                raise ValueError
            if sizes and vendor_code:
                price = float(sizes[0]['price'])
                if not math.isfinite(price):
                    raise ValueError
                vendor_code_to_price[vendor_code] = price
                vendor_code_to_nm_id[vendor_code] = item['nmID']
        except (KeyError, TypeError, ValueError, OverflowError):
            raise ApiError('Wildberries (цены): некорректная цена или карточка в ответе API.') from None

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
    """Отправляет изменения цен WB и возвращает текущие цены для Excel."""
    vendor_code_to_price, vendor_code_to_nmID = get_current_prices_wb()
    data = {'data': []}
    skipped = Counter()

    for vendor_code, delta in article_info.items():
        current_price = vendor_code_to_price.get(vendor_code)
        nm_id = vendor_code_to_nmID.get(vendor_code)

        if current_price is None:
            skipped['нет текущей цены'] += 1
            continue
        if nm_id is None:
            skipped['нет nmID'] += 1
            continue

        try:
            new_price = current_price + delta
            if not math.isfinite(new_price) or new_price < 1:
                raise ValueError
        except (ValueError, TypeError, OverflowError):
            skipped['некорректная итоговая цена'] += 1
            continue

        data['data'].append({
            'nmID': int(nm_id),
            'price': int(new_price),
            'discount': 0
        })

    if data['data']:
        result = wb_json('POST', API_URLS_WB['upload_task'], 'prices',
                         json=data, statuses=(200, 208), retry=False)
        task = result.get('data') if isinstance(result, dict) else None
        if not isinstance(task, dict) or result.get('error') is not False or type(task.get('id')) is not int:
            raise ApiError('Wildberries: API не подтвердил приём задачи обновления цен.')

    print(f'Wildberries (цены): принято к обработке — {len(data["data"])}, пропущено — {sum(skipped.values())}.')
    for reason, count in skipped.items():
        print(f'  {reason} — {count}.')
    return vendor_code_to_price


def write_price_to_excel(current_prices: dict, marketplace='ОЗОН', *, path=DATA_WORKBOOK) -> None:
    """Записывает текущие цены в столбец F указанной книги."""
    write_price_sheets_to_excel({marketplace: current_prices}, path=path)


def write_price_sheets_to_excel(prices_by_sheet: dict, *, path=DATA_WORKBOOK) -> None:
    """Сохраняет текущие цены на всех указанных листах одной заменой файла."""
    wb = load_workbook(find_workbook(path))
    try:
        for marketplace, current_prices in prices_by_sheet.items():
            if marketplace not in wb.sheetnames:
                raise ValueError(f'В книге «{path}» нет листа «{marketplace}».')
            ws = wb[marketplace]
            for row in ws.iter_rows(min_row=4):
                cell_article = row[1].value
                if not cell_article:
                    continue
                offer_id = str(cell_article).strip()
                price_value = current_prices.get(offer_id)
                if price_value is not None:
                    ws.cell(row=row[1].row, column=6, value=price_value)
        save_workbook(wb, path)
    finally:
        wb.close()
    print(f'✅ Текущие цены успешно записаны в {path}')
