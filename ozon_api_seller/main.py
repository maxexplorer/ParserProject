import os
import time
from datetime import datetime, timedelta
import glob

import requests
import pandas as pd

from configs.config import CLIENT_ID, API_KEY, API_URL


def get_cutoff_range(days: int = 7):
    cutoff_to = datetime.utcnow()
    cutoff_from = cutoff_to - timedelta(days=days)
    return cutoff_from.isoformat() + 'Z', cutoff_to.isoformat() + 'Z'


def fetch_orders(cutoff_from: str, cutoff_to: str):
    headers = {
        'Client-Id': CLIENT_ID,
        'Api-Key': API_KEY
    }

    json = {
        'dir': 'ASC',
        'filter': {
            'cutoff_from': cutoff_from,
            'cutoff_to': cutoff_to,
            'status': 'awaiting_packaging'
        },
        'limit': 100,
        'offset': 0,
        'with': {
            'analytics_data': True,
            'barcodes': True,
            'financial_data': True,
            'translit': True
        }
    }

    try:
        time.sleep(1)
        response = requests.post(API_URL, headers=headers, json=json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'❌ Ошибка HTTP: {err}')
    except Exception as e:
        print(f'❌ Общая ошибка: {e}')
    return None


def load_article_prices_from_excel(folder='data'):
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    path = excel_files[0]  # Берём первый найденный
    print(f'📄 Загружаю Excel: {path}')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    df = df.dropna(subset=['Артикул', df.columns[2]])

    return {
        str(row['Артикул']).strip(): row.iloc[2]
        for _, row in df.iterrows()
    }


def extract_data(postings: list, article_prices: dict):
    data = []
    for post in postings:
        product = post.get('products', [{}])[0]
        offer_id = str(product['offer_id']).strip()

        # Пропускаем, если цены нет в article_prices
        if offer_id not in article_prices:
            continue

        name = product['name']
        quantity = product['quantity']

        price = article_prices[offer_id]

        data.append({
            'Артикул': offer_id,
            'Наименование': name,
            'Цена': price,
            'Количество': quantity
        })
    return data


def save_excel(data, filename_prefix='results/ozon_orders'):
    now_str = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"{filename_prefix}_{now_str}.xlsx"

    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f'✅ Данные сохранены в {filename}')


def main():
    print('📦 Получение заказов с Ozon...')
    cutoff_from, cutoff_to = get_cutoff_range(7)
    print(f'⏱ Период: {cutoff_from} → {cutoff_to}')

    result = fetch_orders(cutoff_from, cutoff_to)
    if not result:
        return

    postings = result.get('result', {}).get('postings', [])
    if not postings:
        print('❗ Заказов со статусом "awaiting_packaging" не найдено.')
        return

    article_prices = load_article_prices_from_excel()
    data = extract_data(postings, article_prices)
    save_excel(data)


if __name__ == '__main__':
    main()
