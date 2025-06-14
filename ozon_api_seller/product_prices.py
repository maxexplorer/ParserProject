# product_prices.py

import requests
import pandas as pd
import time

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import load_article_prices_from_excel

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY
}


def get_all_products():
    all_products = []
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

        print(f'Всего продуктов: {total}')

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


def get_prices_and_commissions(offer_id: list) -> list:
    article_prices = load_article_prices_from_excel()

    """Получение цен и комиссий через /v5/product/info/prices"""
    filter = {
        'offer_id': ['2004'],
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

            expenses_fbo = marketing_price - (
                        acquiring + fbo_deliv_to_customer_amount + fbo_direct_flow_trans_average_amount)
            expenses_fbs = marketing_price - (
                        acquiring + fbs_deliv_to_customer_amount + fbs_direct_flow_trans_max_amount + fbs_first_mile_max_amount)

        cursor = data.get('cursor', '')
        if not cursor:
            break

        time.sleep(0.1)  # для защиты от лимитов

    return result_data


def main():
    offer_id = get_all_products()
    net_profit = get_prices_and_commissions(offer_id=offer_id)


if __name__ == '__main__':
    main()
