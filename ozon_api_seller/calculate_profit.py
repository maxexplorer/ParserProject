# calculate_profit.py
import time
import os
import glob

import requests
import pandas as pd

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_excel

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY
}


def get_all_products():
    all_products = []
    last_id = ''
    limit = 100

    total_printed = False

    while True:
        payload = {
            'filter': {
                'visibility': 'IN_SALE'
            },
            'last_id': last_id,
            'limit': limit
        }

        response = requests.post(
            API_URLS.get('product_list'),
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print('❌ Ошибка:', response.status_code, response.text)
            break

        data = response.json()
        result = data.get('result', [])
        items = result.get('items', [])
        total = result.get('total')

        if not total_printed:
            print(f'Всего продуктов: {total}')
            total_printed = True

        for item in items:
            product_id = item.get('product_id')
            offer_id = item.get('offer_id')

            all_products.append(
                offer_id
            )

        # Обновляем last_id для следующей страницы
        last_id = result.get('last_id', '')
        if not last_id:
            break

        time.sleep(1)  # 🔁 пауза между запросами, чтобы не попасть под лимит

    return all_products


def load_article_info_from_excel(folder: str = 'data') -> dict:
    """
    Возвращает {offer_id: (name, price)}
    """
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    df = pd.read_excel(excel_files[0])
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Артикул', df.columns[1], df.columns[2]])

    return {
        str(row['Артикул']).strip(): (str(row.iloc[1]).strip(), row.iloc[2])
        for _, row in df.iterrows()
    }


def get_prices_and_commissions(offer_id: list, article_info: dict) -> list:
    """Получение цен и комиссий через /v5/product/info/prices"""
    filter = {
        'offer_id': offer_id,
        'product_id': []
    }

    result_data = []
    cursor = ''
    limit = 100

    while True:
        payload = {
            'cursor': cursor,
            'filter': filter,
            'limit': limit
        }

        response = requests.post(
            API_URLS.get('product_info_prices'),
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print('Ошибка:', response.status_code, response.text)
            break

        data = response.json()

        items = data.get('items', [])
        for item in items:
            acquiring = item.get('acquiring')
            offer_id = item.get('offer_id')
            commissions = item.get('commissions')
            fbo_deliv_to_customer_amount = commissions.get('fbo_deliv_to_customer_amount')
            fbo_direct_flow_trans_max_amount = commissions.get('fbo_direct_flow_trans_max_amount')
            fbo_direct_flow_trans_min_amount = commissions.get('fbo_direct_flow_trans_min_amount')
            fbo_direct_flow_trans_average_amount = (
                                                           fbo_direct_flow_trans_max_amount + fbo_direct_flow_trans_min_amount) / 2

            fbs_deliv_to_customer_amount = commissions.get('fbs_deliv_to_customer_amount')
            fbs_direct_flow_trans_max_amount = commissions.get('fbs_direct_flow_trans_max_amount')
            fbs_first_mile_max_amount = commissions.get('fbs_first_mile_max_amount')
            marketing_price = item.get('price').get('marketing_price')

            expenses_fbo = acquiring + fbo_deliv_to_customer_amount + fbo_direct_flow_trans_average_amount
            expenses_fbs = acquiring + fbs_deliv_to_customer_amount + fbs_direct_flow_trans_max_amount + fbs_first_mile_max_amount

            name, price = article_info.get(offer_id, ('', 0))

            if name and price:
                expenses_fbo = price + expenses_fbo
                net_profit_fbo = marketing_price - expenses_fbo
                expenses_fbs = price + expenses_fbs
                net_profit_fbs = marketing_price - expenses_fbs

            else:
                expenses_fbo = expenses_fbs = net_profit_fbo = net_profit_fbs = ''

            result_data.append({
                'Артикул': offer_id,
                'Название товара': name,
                'Расходы FBO': expenses_fbo,
                'Расходы FBS': expenses_fbs,
                'Чистая прибыль FBO': net_profit_fbo,
                'Чистая прибыль FBS': net_profit_fbs,
            })

        cursor = data.get('cursor', '')
        if not cursor:
            break

        time.sleep(1)  # для защиты от лимитов

    return result_data


def run_product_prices():
    print("📊 Подсчёт чистой прибыли...")
    offer_id = get_all_products()
    article_info = load_article_info_from_excel()

    result = get_prices_and_commissions(offer_id=offer_id, article_info=article_info)
    if not result:
        print('❗ Нет подходящих товаров для сохранения.')
        return

    save_excel(data=result, filename_prefix='results/ozon_profit')
