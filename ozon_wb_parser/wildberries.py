import json
import os.path

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


def get_data(urls_list):

    # with open(file_path, 'r', encoding='utf-8') as file:
    #     product_urls_list = [line.strip() for line in file.readlines()]

    # with Session() as session:
    #     for url in urls_list[:1]:
    #         id_brand = get_id_brand(url=url, session=session)
    #
    #
    #         if id_brand is None:
    #             continue
    #
    # headers = {
    #     'Accept': '*/*',
    #     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    #     'Connection': 'keep-alive',
    #     'Origin': 'https://www.wildberries.ru',
    #     'Referer': url,
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'cross-site',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    #     'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    #
    # params = {
    #     'appType': '1',
    #     'brand': id_brand,
    #     'curr': 'rub',
    #     'dest': '-1257786',
    #     'sort': 'popular',
    #     'spp': '30',
    # }
    #
    # response = requests.get('https://catalog.wb.ru/brands/b/catalog', params=params, headers=headers)
    #
    # if not os.path.exists('data'):
    #     os.makedirs('data')
    #
    # with open('data/data_json.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    with open('data/data_json.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    prod_items = json_data['data']['products']

    for item in prod_items:
        brand = item['brand']
        name = item['name']
        sku = item['id']


        print(brand, name, sku)




def main():

    get_data(urls_list=urls_list)


if __name__ == '__main__':
    main()
