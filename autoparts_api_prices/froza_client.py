# froza_client.py

"""
Модуль работы с Froza XML API.

Поиск товаров через search_xml4.php (price_list).
"""

import time
import xml.etree.ElementTree as ET

import requests

from utils import (
    safe_float,
    safe_int
)


class FrozaClient:
    """
    Клиент для работы с Froza API.
    """

    def __init__(self, url: str, login: str, password: str, headers: dict):
        self.url = url
        self.login = login
        self.password = password
        self.headers = headers

    def build_url(self, article: str) -> str:
        return (
            f"{self.url}"
            f"?get=price_list"
            f"&user={self.login}"
            f"&password={self.password}"
            f"&code={article}"
        )

    def get_data(self, articles: list, client_name: str, interval: float = 1.0) -> list:
        """
        Получение данных по артикулам.

        :param articles: список [(article, brand), ...]
        :param interval: задержка между запросами
        :return: список словарей
        """

        results = []
        total = len(articles)

        for i, (article, brand) in enumerate(articles, start=1):

            url = self.build_url(article)

            try:
                time.sleep(interval)
                response = requests.get(url=url, headers=self.headers, timeout=20)
                response.raise_for_status()
            except requests.exceptions.RequestException as ex:
                print(f"❌ Froza ошибка запроса: {ex}")
                continue

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError:
                print(f"❌ Froza ошибка XML")
                continue

            # собираем все предложения для артикула
            offers = []
            for item in root.findall('.//item'):
                price = safe_float(item.findtext('price'))
                if price is None:
                    continue
                quantity = safe_int(item.findtext('quantity'))
                description = item.findtext('description_rus') or item.findtext('description')
                offers.append({
                    'Артикул': article,
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': description
                })

            if not offers:
                print(f"❌ Froza {article} ничего не найдено")
                continue

            # выбираем минимальную цену
            min_offer = min(offers, key=lambda x: x['Цена'])

            results.append({
                'Артикул': article,
                'Цена': min_offer['Цена'],
                'Количество': min_offer['Количество'],
                'Наименование производителя': min_offer['Наименование производителя'],
            })

            print(f"📦 Froza {client_name} {i}/{total} артикулов")

        return results
