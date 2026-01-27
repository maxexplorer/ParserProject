# get_products.py

import time
import requests

from configs.config import API_URLS_OZON, OZON_HEADERS
from configs.config import API_URLS_WB, WB_PRICES_AND_DISCOUNTS_HEADERS


def get_all_products_ozon() -> dict[int, str]:
    """
    Получает все товары OZON с помощью API v3/product/list.
    Возвращает словарь:
    {
        product_id: offer_id,
        ...
    }
    """

    result: dict[int, str] = {}
    last_id = ''
    limit = 100

    while True:
        payload = {
            "filter": {
                "visibility": "ALL"
            },
            "last_id": last_id,
            "limit": limit
        }

        try:
            time.sleep(1)  # небольшая пауза для API
            response = requests.post(
                API_URLS_OZON['product_list'],
                headers=OZON_HEADERS,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Ошибка API при получении товаров OZON: {e}")
            break

        data = response.json()
        items = data.get('result', {}).get('items', [])
        if not items:
            break

        for item in items:
            product_id = item.get('product_id')
            offer_id = item.get('offer_id')
            if product_id and offer_id:
                result[product_id] = offer_id

        last_id = data.get('result', {}).get('last_id')
        if not last_id:
            break

    return result


def get_all_products_wb() -> dict[int, str]:
    """
    Получает все товары WB через API v2/list/goods/filter.
    Возвращает словарь:
    {
        nmID: vendorCode,
        ...
    }
    """
    result: dict[int, str] = {}
    limit = 1000
    offset = 0

    while True:
        params = {
            "limit": limit,
            "offset": offset
        }

        try:
            time.sleep(1)  # защита от лимитов
            response = requests.get(
                API_URLS_WB['list_goods_filter'],
                headers=WB_PRICES_AND_DISCOUNTS_HEADERS,
                params=params,
                timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Ошибка WB API: {e}")
            break

        data = response.json()
        goods = data.get("data", {}).get("listGoods", [])
        if not goods:
            break

        for item in goods:
            nm_id = item.get("nmID")
            vendor_code = item.get("vendorCode")
            if nm_id and vendor_code:
                result[nm_id] = vendor_code

        offset += limit

    return result


def run_main_ozon():
    products = get_all_products_ozon()
    print(f"Всего товаров: {len(products)}")
    for product_id, offer_id in products.items():
        print(f"{product_id}: {offer_id}")


def run_main_wb():
    products = get_all_products_wb()
    print(f"Всего товаров WB: {len(products)}")
    for nm_id, vendor_code in products.items():
        print(f"{nm_id}: {vendor_code}")


# Для ручного теста
if __name__ == "__main__":
    run_main_wb()
