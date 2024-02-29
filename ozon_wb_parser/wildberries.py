import json
import os.path
import time
from math import floor

import requests
from requests import Session

urls_list = [
    "https://www.wildberries.ru/brands/97714537-belgatto",
    "https://www.wildberries.ru/brands/rifforma"
]


def get_id_brand(url: str, session: Session) -> int:

    headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': url,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    brand = url.split('brands')[-1].strip()

    response = session.get(f'https://static-basket-01.wbbasket.ru/vol0/data/brands{brand}.json', headers=headers)

    json_data = response.json()

    id_brand = json_data.get('id')

    return id_brand


def get_data_products(urls_list):

    # with open(file_path, 'r', encoding='utf-8') as file:
    #     product_urls_list = [line.strip() for line in file.readlines()]

    with Session() as session:
        for url in urls_list[:1]:

            time.sleep(1)

            id_brand = get_id_brand(url=url, session=session)

            if id_brand is None:
                continue

            headers = {
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Origin': 'https://www.wildberries.ru',
                'Referer': url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'appType': '1',
                'brand': id_brand,
                'curr': 'rub',
                'dest': '-1257786',
                'sort': 'popular',
                'spp': '30',
            }

            response = session.get('https://catalog.wb.ru/brands/b/catalog', params=params, headers=headers)

            if not os.path.exists('data'):
                os.makedirs('data')

        # with open('data/data_json.json', 'w', encoding='utf-8') as file:
        #     json.dump(response.json(), file, indent=4, ensure_ascii=False)
        #
        # with open('data/data_json.json', 'r', encoding='utf-8') as file:
        #     json_data = json.load(file)

            json_data = response.json()

            prod_items = json_data['data']['products']

            for item in prod_items[:1]:
                brand = item['brand']
                name = item['name']
                id_product = str(item['id'])
                colors = ', '.join(c['name'] for c in item['colors'])
                sale_price = item['salePriceU'] // 100
                reviewRating = item['reviewRating']
                rating = item['rating']
                feedbacks = item['feedbacks']
                wb_price = floor(sale_price * 0.97)

                print('###################################################')
                print(f'brand: {brand}')
                print(f'name: {name}')
                print(f'sku: {id_product}')
                print(f'colors: {colors}')
                print(f'sale_price: {sale_price}')
                print(f'reviewRating: {reviewRating}')
                print(f'rating: {rating}')
                print(f'feedbacks: {feedbacks}')
                print(f'wb_price: {wb_price}')

                get_card_product(id_product=id_product, session=session)


def get_card_product(id_product=None, session=None):

    # headers = {
    #     'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    #     'Referer': f'https://www.wildberries.ru/catalog/{id_product}/detail.aspx',
    #     'sec-ch-ua-mobile': '?0',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    #
    # response = requests.get(f'https://basket-10.wbbasket.ru/vol{id_product[:-5]}/part{id_product[:-3]}/{id_product}/info/ru/card.json',
    #                         headers=headers)
    #
    # with open('data/product_data_json.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    with open('data/product_data_json.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    imt_id = str(json_data['imt_id'])
    colors = json_data['nm_colors_names']

    get_feedbacks(imt_id)



def get_feedbacks(imt_id=None):



    # response = requests.get(f'https://feedbacks1.wb.ru/feedbacks/v1/{imt_id}')


    # with open('data/feedbacks_json.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    with open('data/feedbacks_json.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    json_data = json_data['feedbacks']



    # Сортировка списка словарей по дате
    sorted_list_of_dicts = sorted([i for i in json_data], key=extract_date, reverse=True)

    # Вывод отсортированного списка словарей
    res = sum(item['productValuation'] for item in sorted_list_of_dicts[:5]) / 5

    print(res)


# Функция для извлечения даты из строки и преобразования в объект datetime
from datetime import datetime
def extract_date(dict_item):
    return datetime.strptime(dict_item['createdDate'], "%Y-%m-%dT%H:%M:%SZ")


def main():

    # get_data_products(urls_list=urls_list)
    # get_feedbacks()
    get_card_product()

if __name__ == '__main__':
    main()
