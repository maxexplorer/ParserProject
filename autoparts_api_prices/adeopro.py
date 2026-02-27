import time
import xml.etree.ElementTree as ET

import requests

from utils import chunked


class AdeoproClient:
    """
    Клиент для работы с Adeopro API.
    Поддерживает пакетную проверку артикула + бренда через priceBatch.
    """

    def __init__(self, url: str, login: str, password: str, headers: dict = None):
        self.url = url
        self.login = login
        self.password = password
        self.headers = headers

    def get_data(self, articles: list, interval: float = 1.0) -> list:
        """
        Получение цен и остатков для списка (article, brand)
        articles: список кортежей [(article, brand), ...]
        interval: интервал между пакетными запросами
        """
        results = []
        batch_size = 100  # можно регулировать по документации
        total_batches = (len(articles) + batch_size - 1) // batch_size

        for batch_num, batch in enumerate(chunked(articles, batch_size), start=1):
            xml_payload = self.build_xml(batch)
            try:
                response = requests.post(
                    url=self.url,
                    headers=self.headers,
                    data={"xml": xml_payload},
                    timeout=60
                )
                response.raise_for_status()
                data = response.text
                results.extend(self.parse_response(data))
            except requests.RequestException as ex:
                print(f"❌ Adeopro батч {batch_num}/{total_batches} ошибка: {ex}")
                continue

            print(f"📦 Adeopro батч {batch_num}/{total_batches} ({len(batch)} артикулов)...")
            time.sleep(interval)

        return results

    def build_xml(self, batch: list) -> str:
        """
        Формирует XML для batch запроса
        """
        items_xml = "".join(
            f"<items><pn>{article}</pn><brand>{brand}</brand></items>"
            for article, brand in batch
        )

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <message>
            <param>
                <action>priceBatch</action>
                <login>{self.login}</login>
                <password>{self.password}</password>
            </param>
            {items_xml}
        </message>"""
        return xml

    @staticmethod
    def parse_response(xml_data: str) -> list:
        """
        Парсинг ответа XML. Возвращает список словарей:
        [{'Артикул': article, 'Цена': price, 'Количество': quantity, 'Наименование производителя': name}, ...]
        """
        results = []
        try:
            root = ET.fromstring(xml_data)
            for detail in root.findall('detail'):
                stock_element = detail.find('stock')
                price_element = detail.find('price')
                article_element = detail.find('code')
                brand_element = detail.find('producer')

                # Пропуск "Cella2108", если нужно
                if stock_element is not None and "Cella2108" in stock_element.text:
                    continue

                article = article_element.text if article_element is not None else ""
                brand = brand_element.text if brand_element is not None else ""
                price = float(price_element.text) if price_element is not None else 0.0

                # Остатки
                rest_element = detail.find('rest')
                quantity = int(rest_element.text) if rest_element is not None else 0

                results.append({
                    'Артикул': article,
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': brand,
                })
        except ET.ParseError as ex:
            print(f"Ошибка разбора XML: {ex}")

        return results
