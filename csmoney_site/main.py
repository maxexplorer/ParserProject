import requests
from fake_useragent import UserAgent
import json
import os

useragent = UserAgent()

# url = "https://cs.money/ru/market/buy/"
url = "https://cs.money/1.0/market/sell-orders?limit=60&offset=0&type=5"

headers = {
    'User-Agent': useragent.random
}


def get_json(url, headers):
    response = requests.get(url=url, headers=headers)

    data = response.json()

    return data


def collect_data(data):
    result_lst = []

    items = data['items']

    for item in items:
        item_id = item['id']
        item_name = item['asset']['names']['full']
        item_img = item['asset']['images']['steam']
        item_price_computed = item['pricing']['computed']
        item_price_default = item['pricing']['default']
        item_discount = round(item['pricing']['discount'] * 100, 2)
        result_lst.append(
            {
                'id': item_id,
                'name': item_name,
                'img': item_img,
                'price_computed': item_price_computed,
                'price_default': item_price_default,
                'discount': item_discount
            }
        )
    return result_lst


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    cards = []
    type = 5
    pages = int(input('Введите количество страниц: '))
    for page in range(0, pages * 60, 60):
        print(f'Парсинг страницы: {page // 60 + 1}')
        url = f"https://cs.money/1.0/market/sell-orders?limit=60&offset={page}&type={type}"
        data = get_json(url=url, headers=headers)
        cards.extend(collect_data(data))
    save_json(cards)


if __name__ == '__main__':
    main()
