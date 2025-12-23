# abcp.py

import time
import requests

from utils import chunked


def get_prices_abcp(
        url: str,
        headers: dict,
        userlogin: str,
        userpsw: str,
        articles: list
):
    """
    Поиск цен в ABCP через search/batch
    """

    url = f'{url}search/batch'

    results = []

    total_batches = (len(articles) + 99) // 100  # максимум 100 в batch
    batch_num = 0

    for batch in chunked(articles, 100):
        batch_num += 1

        payload = {
            "userlogin": userlogin,
            "userpsw": userpsw,
        }

        # формируем search[i][number], search[i][brand]
        for i, (article, brand) in enumerate(batch):
            payload[f"search[{i}][number]"] = article
            payload[f"search[{i}][brand]"] = brand

        try:
            time.sleep(1)

            response = requests.post(
                url=url,
                headers=headers,
                data=payload,
                timeout=30
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as ex:
            print(
                f'❌ ABCP батч {batch_num}/{total_batches} '
                f'ошибка запроса: {ex}'
            )
            continue

        try:
            data = response.json()
        except ValueError:
            print(
                f'❌ ABCP батч {batch_num}/{total_batches} '
                f'ошибка JSON'
            )
            continue

        if not data:
            continue

        for item in data:
            article = item.get('number')
            brand = item.get('brand')
            price = item.get('price')
            description = item.get('description')

            results.append(
                {
                    'Артикул': article,
                    'Цена': price,
                }
            )

        print(f'📦 ABCP батч {batch_num}/{total_batches} ({len(data)} артикулов)...')

    return results
