# adeopro.py

import time
import xml.etree.ElementTree as ET
import requests

from utils import (
    safe_float,
    safe_int
)


class AdeoproClient:
    def __init__(self, url: str, login: str, password: str, headers: dict = None):
        self.url = url
        self.login = login
        self.password = password
        self.headers = headers

    def get_data(self, articles: list, client_name: str, interval: float = 1.0) -> list:
        """
        Одиночный запрос по каждому артикулу (как Froza)
        """
        results = []
        total = len(articles)

        for i, (article, brand) in enumerate(articles, start=1):

            xml_payload = self.build_xml(article, brand)

            try:
                time.sleep(interval)

                response = requests.post(
                    url=self.url,
                    headers=self.headers,
                    data={"xml": xml_payload},
                    timeout=30
                )
                response.raise_for_status()

            except requests.RequestException as ex:
                print(f"❌ Adeopro {article} ошибка запроса: {ex}")
                continue

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError:
                print(f"❌ Adeopro {article} ошибка XML")
                continue

            # собираем все предложения
            offers = []

            for detail in root.findall('.//detail'):
                price = safe_float(detail.findtext('price'))
                if price is None:
                    continue

                quantity = safe_int(detail.findtext('rest'))
                description = detail.findtext('caption')
                stock = detail.findtext('stock')
                delivery = safe_int(detail.findtext('delivery'))
                percent_refuse = safe_int(detail.findtext('PercentRefuse'))
                good_return = detail.findtext('good_return')

                if (
                        delivery > 3 or
                        percent_refuse > 30 or
                        stock == "Cella2108" or
                        good_return != "Возврат без уценки"
                ):
                    continue

                offers.append({
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': description
                })

            if not offers:
                print(f"❌ Adeopro {article} ничего не найдено")
                continue

            # выбираем минимальную цену
            min_offer = min(offers, key=lambda x: x['Цена'])

            results.append({
                'Артикул': article,
                'Цена': min_offer['Цена'],
                'Количество': min_offer['Количество'],
                'Наименование производителя': min_offer['Наименование производителя'],
            })

            print(f"📦 Adeopro {client_name} {i}/{total} артикулов")

        return results

    def build_xml(self, article: str, brand: str) -> str:
        """
        XML для одного артикула
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <message>
            <param>
                <action>price</action>
                <login>{self.login}</login>
                <password>{self.password}</password>
                <code>{article}</code>
                <brand>{brand}</brand>
                <crosses>disallow</crosses>
            </param>
        </message>"""
