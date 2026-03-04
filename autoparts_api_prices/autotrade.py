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

from utils import (
    chunked,
    safe_float,
    safe_int
)


class AutotradeClient:
    """
    Клиент для работы с Autotrade API.
    """

    def __init__(self, url: str, login: str, password: str, headers: dict):
        self.url = url
        self.auth_key = self._generate_auth_key(login, password)
        self.headers = headers

    @staticmethod
    def _generate_auth_key(login, password) -> str:
        salt = '1>6)/MI~{J'
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        return hashlib.md5((login + password_md5 + salt).encode('utf-8')).hexdigest()

    def get_data(self, articles: list, client_name: str, interval: float=1.0) -> list:
        """
        Получение цен и остатков для списка (article, brand)
        """
        results = []
        # Autotrade принимает до 60 позиций за запрос
        batch_size = 60
        total_batches = (len(articles) + batch_size - 1) // batch_size

        for batch_num, batch in enumerate(chunked(articles, batch_size), start=1):
            batch_num += 1
            items_payload = {article: {brand: 1} for article, brand in batch}

            payload = {
                "auth_key": self.auth_key,
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
                time.sleep(interval)
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
                price: float = safe_float(item.get('price'))
                quantity: int = safe_int(self.get_quantity(item))

                results.append({
                    'Артикул': article,
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': name,
                })

            print(f"📦 Autotrade {client_name} батч {batch_num}/{total_batches} ({len(items)} артикулов)...")

        return results

    @staticmethod
    def get_quantity(item: dict) -> int:
        total_quantity_packed = 0
        total_quantity_unpacked = 0

        for stock_id, stock_info in item.get('stocks', {}).items():
            total_quantity_packed += stock_info.get('quantity_packed', 0)
            total_quantity_unpacked += stock_info.get('quantity_unpacked', 0)

        quantity = total_quantity_packed + total_quantity_unpacked

        return quantity
