import requests
import pandas as pd
from datetime import datetime, timedelta
from configs.config import CLIENT_ID, API_KEY, API_URL


def get_cutoff_range(days: int = 7):
    """Возвращает дату cutoff_from и cutoff_to в формате ISO8601"""
    cutoff_to = datetime.utcnow()
    cutoff_from = cutoff_to - timedelta(days=days)
    return cutoff_from.isoformat() + "Z", cutoff_to.isoformat() + "Z"


def fetch_orders(cutoff_from: str, cutoff_to: str):
    headers = {
        "Client-Id": CLIENT_ID,
        "Api-Key": API_KEY
    }

    json = {
        "dir": "ASC",
        "filter": {
            "cutoff_from": cutoff_from,
            "cutoff_to": cutoff_to,
            "status": "awaiting_packaging"
        },
        "limit": 100,
        "offset": 0,
        "with": {
            "analytics_data": True,
            "barcodes": True,
            "financial_data": True,
            "translit": True
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'❌ Ошибка HTTP: {err}')
    except Exception as e:
        print(f'❌ Общая ошибка: {e}')
    return None


def extract_data(postings: list):
    data = []
    for post in postings:
        product = post.get("products", [{}])[0]
        sku = product["sku"]
        price = product["price"]
        quantity = product["quantity"]
        total_quantity = price * quantity

        data.append({
            'Артикул': sku,
            'Цена': price,
            'Наименование': name,
            'Количество': quantity
        })
    return data


def save_to_excel(data, filename="ozon_orders.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"✅ Данные сохранены в {filename}")


def main():
    print("📦 Получение заказов с Ozon...")
    cutoff_from, cutoff_to = get_cutoff_range(7)
    print(f"⏱ Период: {cutoff_from} → {cutoff_to}")

    result = fetch_orders(cutoff_from, cutoff_to)
    if not result:
        return

    postings = result.get("result", {}).get("postings", [])
    if not postings:
        print("❗ Заказов со статусом 'awaiting_packaging' не найдено.")
        return

    data = extract_data(postings)
    save_to_excel(data)


if __name__ == "__main__":
    main()
