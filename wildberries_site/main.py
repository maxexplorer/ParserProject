import requests
from bs4 import BeautifulSoup
import os
import time
import json

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/108.0.0.0 Safari/537.36'
}


def get_data(headers):
    result_list = []

    product = 'кофе'

    for i in range(1, 2):
        page = i
        url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=3,6,19,21,8&curr=rub&dest=-1059500,-72639,-1754564,-4653095&emp=0&lang=ru&locale=ru&{page=}&pricemarginCoeff=1.0&query={product}&reg=0&regions=80,64,83,4,38,33,86,30,40,48,1,66,31,68,22&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"

        response = requests.get(url=url, headers=headers)

        data = response.json()
        items = data['data']['products']

        for item in items:
            result_list.append(
                {
                    'title': item.get('name'),
                    'brand': item.get('brand'),
                    'sale': item.get('sale'),
                    'price': item.get('priceU') // 100,
                    'sale_price': item.get('salePriceU') // 100,
                    'rating': item.get('rating')

                }
            )

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/result_list.json', 'w', encoding='utf-8') as file:
            json.dump(result_list, file, indent=4, ensure_ascii=False)


def main():
    get_data(headers=headers)


if __name__ == '__main__':
    main()
