# autotrade.py

"""
Модуль работы с Autotrade API.

Получение цен и остатков товаров
через метод getStocksAndPrices.
"""

import time
import json
import hashlib

import requests

from utils import chunked


class AutotradeClient:
    """
    Клиент для работы с Autotrade API.
    """

    def __init__(self, url: str, login: str, password: str, headers: dict):
        self.url = url
        self.login = login
        self.password = password
        self.headers = headers

        self.salt = '1>6)/MI~{J'  # как в config

    def _generate_auth_key(self) -> str:
        """
        Генерирует auth_key на основе логина и пароля.
        """
        password_md5 = hashlib.md5(self.password.encode('utf-8')).hexdigest()
        auth_key = hashlib.md5((self.login + password_md5 + self.salt).encode('utf-8')).hexdigest()
        return auth_key

    def get_prices(self, articles: list) -> list:
        """
        Получение цен и остатков для списка (article, brand)
        """
        results = []
        auth_key = self._generate_auth_key()
        total_batches = (len(articles) + 59) // 60
        batch_num = 0

        for batch in chunked(articles, 60):
            batch_num += 1
            items_payload = {article: {brand: 1} for article, brand in batch}

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
                    url=self.url,
                    headers=self.headers,
                    data="data=" + json.dumps(payload),
                    timeout=30
                )
                response.raise_for_status()
            except requests.RequestException as ex:
                print(f"❌ Autotrade батч {batch_num}/{total_batches} ошибка: {ex}")
                continue

            try:
                data = response.json()
            except ValueError:
                print(f"❌ Autotrade батч {batch_num}/{total_batches} ошибка JSON")
                continue

            items = data.get('items', {})

            if not items:
                continue

            for _, item in items.items():
                article: str = item.get('article')
                brand: str = item.get('brand')
                name: str = item.get('name')
                price: float = item.get('price')

                results.append({
                    'Артикул': article,
                    'Цена': price,
                    'Источник': 'Autotrade'
                })

            print(f"📦 Autotrade батч {batch_num}/{total_batches} ({len(items)} артикулов)...")

        return results