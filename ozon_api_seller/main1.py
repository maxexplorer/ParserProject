import requests
import pandas as pd
import time

from configs.config import CLIENT_ID, API_KEY, API_URLS

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY
}

# Фильтр: сюда можно вставлять свои offer_id или product_id
filter = {
    'offer_id': ['13650'],  # Пример: ['356792']
    'product_id': [],  # Пример: ['243686911']
    'visibility': 'ALL'
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

        for item in items:
            product_id = item.get('product_id')
            offer_id = item.get('offer_id')

            all_products.append(
                {
                    'product_id': product_id,
                    'offer_id': offer_id,
                }
            )

        # Обновляем last_id для следующей страницы
        last_id = result.get('last_id')
        if not last_id:
            break

        time.sleep(1)  # 🔁 пауза между запросами, чтобы не попасть под лимит

    return all_products


def get_prices_and_commissions():
    """Получение цен и комиссий через /v5/product/info/prices"""
    result = []
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
            commissions = item.get('commissions', {})
            price = item.get('price').get('price')
            old_price = item.get('price').get('old_price')

        cursor = data.get('next_cursor', '')
        if not cursor:
            break

        time.sleep(0.1)  # для защиты от лимитов

    return result


def main():
    products = get_all_products()
    prices = get_prices_and_commissions()


if __name__ == '__main__':
    main()
