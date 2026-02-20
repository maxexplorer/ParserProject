# abcp.py

"""
Модуль работы с ABCP API.

Поиск товаров через операцию search/batch.
"""

import time
import requests

from utils import chunked


def get_prices_abcp(
        url: str,
        headers: dict,
        userlogin: str,
        userpsw: str,
        articles: list
) -> list:
    """
    Поиск цен товаров в ABCP через search/batch.

    :param url: Базовый URL ABCP
    :param headers: HTTP-заголовки
    :param userlogin: Логин пользователя
    :param userpsw: MD5-хэш пароля
    :param articles: Список (article, brand)
    :return: Список словарей с результатами
    """

    # Полный URL операции
    url = f"{url}search/batch"

    results: list = []

    # ABCP принимает до 100 позиций за запрос
    total_batches: int = (len(articles) + 99) // 100
    batch_num: int = 0

    for batch in chunked(articles, 100):
        batch_num += 1

        payload: dict = {
            "userlogin": userlogin,
            "userpsw": userpsw,
        }

        # Формируем параметры search[i][number] и search[i][brand]
        for i, (article, brand) in enumerate(batch):
            payload[f"search[{i}][number]"] = article
            payload[f"search[{i}][brand]"] = brand

        try:
            time.sleep(3)

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
            return results

        try:
            data: list = response.json()
        except ValueError:
            print(
                f'❌ ABCP батч {batch_num}/{total_batches} '
                f'ошибка JSON'
            )
            continue

        if not data:
            continue

        for item in data:
            article: str = item.get('number')
            brand: str = item.get('brand')
            price: float = item.get('price')
            description: str = item.get('description')

            results.append(
                {
                    'Артикул': article,
                    'Цена': price,
                    'Источник': 'ABCP'
                }
            )

        print(
            f'📦 ABCP батч {batch_num}/{total_batches} '
            f'({len(data)} артикулов)...'
        )

    return results
