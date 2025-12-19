import requests
import json





# -------------------
# Получаем цены и остатки пакетом до 60 артикулов
# -------------------
def get_prices_and_stocks(url, headers, auth_key, autotrade_article: list):

    payload = {
        "auth_key": auth_key,
        "method": "getStocksAndPrices",
        "params": {
        "storages": [0],  # 0 = все доступные склады, без кавычек
        "items": {
            autotrade_article: {"SAT": 10}  # пример: артикул + бренд + количество
        },
        "withDelivery": "0",
        "checkTransit": "0",
        "withSubs": "0",
        "strict": "0",
        "original_price": "0",
        "discount": False}
    }

    response = requests.post(url, data="data=" + json.dumps(payload), headers=headers)
    response.raise_for_status()
    items = response.json().get("items", {})

    for item in items:
        print(item)





