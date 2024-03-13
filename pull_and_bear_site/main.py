import json
import os
import time
from datetime import datetime
from random import randint

import requests
from requests import Session
from bs4 import BeautifulSoup

from config import cookies, headers

start_time = datetime.now()


def get_categories():
    categories = []

    # params = {
    #     'languageId': '-1',
    #     'typeCatalog': '1',
    #     'appId': '1',
    # }
    #
    # with Session() as session:
    #     response = session.get(
    #         'https://www.pullandbear.com/itxrest/2/catalog/store/24009400/20309422/category',
    #         params=params,
    #         headers=headers,
    #     )
    #
    # print(response)
    #
    # if not os.path.exists('data'):
    #     os.makedirs('data')
    #
    # with open('data/categories.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    with open('data/categories.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    category_items = json_data['categories']

    for category_item in category_items:
        if category_item.get('name') == 'Woman':
            id_category = category_item.get('id')
            subcategory_items = category_item.get('subcategories')
            for subcategory_item in subcategory_items:
                if subcategory_item.get('name') == 'Clothing':
                    clothing_subcategory_items = subcategory_item.get('subcategories')
                    for clothing_subcategory_item in clothing_subcategory_items:
                        sub_id = clothing_subcategory_item.get('id')
                        sum_name = clothing_subcategory_item.get('name')
                        products_subcategories = clothing_subcategory_item.get('subcategories')

                        if products_subcategories:
                            for prod_sub_cat in products_subcategories:
                                if prod_sub_cat.get('name') == 'See all':
                                    print(f"See all: {prod_sub_cat.get('id')}")
                        else:
                            print(f"id: {clothing_subcategory_item.get('id')}")


def get_subcategories():

    params = {
        'languageId': '-1',
        'showProducts': 'false',
        'appId': '1',
    }

    response = requests.get(
        'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/category/1030204616/product',
        params=params,
        # cookies=cookies,
        headers=headers,
    )
    print(response)

    with open('data/subcategories.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def get_id_products():
    pass


def get_data():
    pass


def main():
    get_categories()
    # get_subcategories()

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
