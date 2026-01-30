# autotrade.py

"""
Модуль работы с Autotrade API.

Получение цен и остатков товаров
через метод getStocksAndPrices.
"""

import time
import json
import requests

from utils import chunked


def get_prices_autotrade(
        url: str,
        headers: dict,
        auth_key: str,
        articles: list
) -> list:
    """
    Получает цены товаров из Autotrade.

    :param url: URL API Autotrade
    :param headers: HTTP-заголовки
    :param auth_key: Ключ авторизации
    :param articles: Список (article, brand)
    :return: Список словарей с результатами
    """

    results: list = []

    # Autotrade принимает до 60 позиций за запрос
    total_batches: int = (len(articles) + 59) // 60
    batch_num: int = 0

    for batch in chunked(articles, 60):
        batch_num += 1

        items_payload: dict = {}

        # Формируем payload items
        for article, brand in batch:
            items_payload[article] = {brand: 1}

        payload: dict = {
            "auth_key": auth_key,
            "method": "getStocksAndPrices",
            "params": {
                "storages": [0],
                "items": items_payload,
                "withDelivery": 0,
                "checkTransit": 0,
                "withSubs": 0,
                "strict": 0,
                "original_price": 0,
                "discount": False
            }
        }

        try:
            time.sleep(1)

            response = requests.post(
                url=url,
                headers=headers,
                data="data=" + json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()

        except Exception as ex:
            print(
                f'❌ Autotrade батч {batch_num}/{total_batches} '
                f'ошибка запроса: {ex}'
            )
            continue

        try:
            data: dict = response.json()
        except ValueError:
            print(
                f'❌ Autotrade батч {batch_num}/{total_batches} '
                f'ошибка JSON'
            )
            continue

        items: dict = data.get('items', {})

        if not items:
            continue

        for _, item in items.items():
            article: str = item.get('article')
            brand: str = item.get('brand')
            name: str = item.get('name')
            price: float = item.get('price')

            results.append(
                {
                    'Артикул': article,
                    'Цена': price,
                }
            )

        print(
            f'📦 Autotrade батч {batch_num}/{total_batches} '
            f'({len(items)} артикулов)...'
        )

    return results
