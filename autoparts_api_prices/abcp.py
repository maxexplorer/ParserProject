# abcp.py

"""
Модуль работы с ABCP API.

Поиск товаров через операцию search/batch.
"""

import time
import hashlib

import requests

from utils import chunked

class ABCPClient:
    """
       Клиент для работы с ABCP API.
       """

    def __init__(self, host: str, login: str, password: str, headers: dict):
        self.host = host
        self.login = login
        self.password_hash = self._generate_hash(password)
        self.headers = headers

    @staticmethod
    def _generate_hash(password: str) -> str:
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def get_data(self, articles: list) -> list:
        """
           Поиск цен товаров в ABCP через search/batch.

           :param url: Базовый URL ABCP
           :param headers: HTTP-заголовки
           :param userlogin: Логин пользователя
           :param userpsw: MD5-хэш пароля
           :param articles: Список (article, brand)
           :return: Список словарей с результатами
           """

        url = f"https://{self.host}/search/batch"

        results: list = []
        # ABCP принимает до 100 позиций за запрос
        batch_size = 100
        total_batches: int = (len(articles) + batch_size - 1) // batch_size

        for batch_num, batch in enumerate(chunked(articles, batch_size), start=1):

            payload = {
                "userlogin": self.login,
                "userpsw": self.password_hash,
            }

            for i, (article, brand) in enumerate(batch):
                payload[f"search[{i}][number]"] = article
                payload[f"search[{i}][brand]"] = brand

            try:
                time.sleep(3)

                response = requests.post(
                    url=url,
                    headers=self.headers,
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
                quantity: int = item.get('availability', 0)

                results.append({
                    'Артикул': article,
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': description,
                })

            print(
                f'📦 ABCP батч {batch_num}/{total_batches} '
                f'({len(data)} артикулов)...'
            )

        return results