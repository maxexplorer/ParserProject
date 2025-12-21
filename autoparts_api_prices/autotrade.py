# autotrade.py

import time
import json

import requests

from utils import chunked


def get_prices_autotrade(
        url: str,
        headers: dict,
        auth_key: str,
        articles: list
):
    results = []

    total_batches = (len(articles) + 59) // 60  # количество батчей
    batch_num = 0

    for batch in chunked(articles, 60):
        batch_num += 1
        print(f'📦 Autotrade батч {batch_num}/{total_batches} ({len(batch)} артикулов)...')

        items_payload = {}

        for article, brand in batch:
            items_payload[article] = {brand: 1}

        payload = {
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
            )
            response.raise_for_status()
        except Exception as ex:
            print(
                f"❌ Autotrade батч {batch_num}/{total_batches} "
                f"ошибка запроса: {ex}"
            )
            continue

        try:
            data = response.json()
        except ValueError:
            print(
                f"❌ Autotrade батч {batch_num}/{total_batches} "
                f"ошибка JSON"
            )
            continue

        items = data.get("items", {})

        if not items:
            continue

        for _, item in items.items():
            article = item.get('article')
            brand = item.get('brand')
            name = item.get('name')
            price = item.get('price')

            results.append(
                {
                    'Артикул': article,
                    'Цена': price,
                }
            )

    return results
