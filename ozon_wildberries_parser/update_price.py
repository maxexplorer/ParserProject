import os
import glob
import json
import time
import pandas as pd
import requests

from configs.config import API_URLS_OZON, API_URLS_WB, OZON_HEADERS, WB_HEADERS


def load_article_info_from_excel(folder='data'):
    """
    Загружает артикулы и new_price из Excel, начиная с 4 строки, артикул в 1 столбце, new_price в 5 столбце.
    :param folder: Папка с Excel
    :return: Словарь {offer_id: delta_price}
    """
    excel_files = glob.glob(os.path.join(folder, '*.xlsm'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsm файлов.')
        return {}

    df = pd.read_excel(excel_files[0], skiprows=3)
    df.columns = df.columns.str.strip()

    article_info = {}
    for _, row in df.iterrows():
        offer_id = str(row.iloc[0]).strip()
        if not offer_id:
            continue

        new_price = row.iloc[4]
        if pd.isna(new_price) or new_price == '':
            continue

        delta = float(new_price)
        article_info[offer_id] = delta

    return article_info


def get_current_prices_ozon():
    """
    Получает текущие маркетинговые цены товаров с Ozon.
    :return: Словарь {offer_id: current_price}
    """
    result = {}
    cursor = ''
    limit = 100

    while True:
        data = {
            'cursor': cursor,
            'filter': {
                'visibility': 'ALL'
            },
            'limit': limit
        }

        try:
            time.sleep(1)
            response = requests.post(
                API_URLS_OZON['product_info_prices'],
                headers=OZON_HEADERS,
                json=data,
                timeout=15
            )
            response.raise_for_status()
        except Exception as ex:
            print(f'❌ Ошибка получения цен Ozon: {ex}')
            break

        try:
            data = response.json()
        except ValueError:
            print(f'❌ Ошибка при декодировании JSON.')
            break

        items = data.get('items', [])
        
        for item in items:
            offer_id = item.get('offer_id')
            price_info = item.get('price', {})
            price = price_info.get('price', 0)
            result[offer_id] = float(price)

        cursor = data.get('last_id')
        if not cursor:
            break

    return result


def get_current_prices_wb():
    """
    Получает текущие цены товаров с WB.
    :return: Словарь {vendorCode: current_price}
    """
    result = {}
    params = {
        'order': 'nmId',
        'direction': 'asc',
        'limit': 100,
        'skip': 0
    }

    while True:
        try:
            time.sleep(1)
            response = requests.get(
                API_URLS_WB['list_goods_filter'],
                headers=WB_HEADERS,
                params=params,
                timeout=15
            )
            response.raise_for_status()
        except Exception as ex:
            print(f'❌ Ошибка получения цен WB: {ex}')
            break

        try:
            data = response.json()
        except ValueError:
            print(f'❌ Ошибка при декодировании JSON.')
            break

        goods = data.get('data', {}).get('listGoods', [])

        if not goods:
            break

        for item in goods:
            vendor_code = item.get('vendorCode')
            sizes = item.get('sizes', [])
            if sizes:
                price = sizes[0].get('price', 0)
                result[vendor_code] = float(price)

        params['skip'] += 100

    return result


def update_prices_ozon():
    """
    Обновляет цены на Ozon по API.
    """
    articles = load_article_info_from_excel()
    if not articles:
        print('Нет данных для обновления цен на Ozon.')
        return

    current_prices = get_current_prices_ozon()
    prices = {'prices': []}

    for offer_id, delta in articles.items():
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
            'vat': '0.1'
        })

    try:
        response = requests.post(
            API_URLS_OZON['import_price'],
            headers=OZON_HEADERS,
            json=payload,
            timeout=20
        )
        print(f'Ozon API: {response.status_code} {response.text}')
    except Exception as ex:
        print(f'❌ Ошибка при обновлении цен Ozon: {ex}')


def update_prices_wb():
    """
    Обновляет цены на Wildberries по API.
    """
    articles = load_article_info_from_excel()
    if not articles:
        print('Нет данных для обновления цен на WB.')
        return

    current_prices = get_current_prices_wb()
    payload = {'data': []}

    for vendor_code, delta in articles.items():
        current_price = current_prices.get(vendor_code)
        if current_price is None:
            print(f'❗ Не найдена текущая цена для WB vendorCode: {vendor_code}')
            continue

        new_price = current_price + delta

        payload['data'].append({
            'nmID': int(vendor_code),
            'price': int(new_price),
            'discount': 30
        })

    try:
        response = requests.post(
            API_URLS_WB['upload_task'],
            headers=WB_HEADERS,
            json=payload,
            timeout=20
        )
        print(f'WB API: {response.status_code} {response.text}')
    except Exception as ex:
        print(f'❌ Ошибка при обновлении цен WB: {ex}')
