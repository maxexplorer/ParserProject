# autotrade.py
import time
import json

import requests

from utils import chunked

def get_prices_and_stocks(url, headers, auth_key, articles: list[tuple[str, str]]):
    print(f'Обрабатывается: Autotrade')

    results = []

    total_batches = (len(articles) + 59) // 60  # количество батчей
    batch_num = 0

    for batch in chunked(articles, 60):
        batch_num += 1
        print(f'Обрабатывается батч {batch_num}/{total_batches} ({len(batch)} артикулов)...')

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

        time.sleep(1)

        response = requests.post(
            url,
            data="data=" + json.dumps(payload),
            headers=headers
        )
        response.raise_for_status()

        data = response.json()
        items = data.get("items", {})

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
