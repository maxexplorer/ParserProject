import json
import os
import time
from datetime import datetime
from random import randint

import requests
from requests import Session
from bs4 import BeautifulSoup

from config import headers, params

start_time = datetime.now()


def get_id_categories():
    id_categories_list = []

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

    for category_item in category_items[:2]:
        category_name = category_item.get('name')
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            if subcategory_item.get('name') == 'Clothing':
                clothing_subcategory_items = subcategory_item.get('subcategories')
                for clothing_subcategory_item in clothing_subcategory_items:
                    id = clothing_subcategory_item.get('id')
                    subcategory_name = clothing_subcategory_item.get('name')
                    if subcategory_name == '-':
                        continue
                    if 'Best sellers' in subcategory_name:
                        break
                    subcategories = clothing_subcategory_item.get('subcategories')
                    if subcategories:
                        for subcategory in subcategories:
                            if subcategory.get('name') == 'See all':
                                id = subcategory.get('id')
                                id_categories_list.append(id)
                    else:
                        id_categories_list.append(id)

                    print(category_name, subcategory_name)

    with open('data/id_categories_list.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_list, file=file, sep='\n')

    return id_categories_list


def get_id_products(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_categories_list = [line.strip() for line in file.readlines()]

    count_categories = len(id_categories_list)

    print(f'Всего: {count_categories} категорий!')

    id_products_list = []
    with Session() as session:
        for i, id_category in enumerate(id_categories_list, 1):
            time.sleep(1)
            response = session.get(
                f'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/category/{id_category}/product',
                params=params,
                headers=headers,
            )

            json_data = response.json()

            product_ids = json_data.get('productIds')

            id_products_list.append(
                {
                    id_category: product_ids
                }
            )

            print(f'Обработано: {i}/{count_categories}')

    with open('data/id_products_list.json', 'w', encoding='utf-8') as file:
        json.dump(id_products_list, file, indent=4, ensure_ascii=False)


def get_products_array(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_products_list = json.load(file)

    for item_dict in id_products_list[1:2]:
        for key in item_dict:
            lst = item_dict[key]
            id_products = ','.join(map(str, lst))

            params = {
                'languageId': '-1',
                'productIds': id_products,
                'categoryId': key,
                'appId': '1',
            }

            response = requests.get(
                'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/productsArray',
                params=params,
                headers=headers,
                )

            with open('data/products_array1.json', 'w', encoding='utf-8') as file:
                json.dump(response.json(), file, indent=4, ensure_ascii=False)


def get_data(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_products_list = json.load(file)

    with Session() as session:
        for id_product in id_products_list[:1]:
                response = session.get(
                    f'https://www.pullandbear.com/itxrest/2/catalog/store/24009400/20309422/category/0/product/'
                    f'{id_product}/detail',
                    params=params,
                    headers=headers,
                )

                json_data = response.json()

        with open('data/product1.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)


    with open('data/product1.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    sku = json_data.get('bundleProductSummaries')




def main():
    # id_categories_list = get_id_categories()
    # id_products_list = get_id_products(file_path='data/id_categories_list.txt')
    # data = get_data(file_path='data/id_products_list.json')
    # get_products_array(file_path='data/id_products_list.json')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


    with open('data/products_array1.json') as file:
        data = json.load(file)

    print(len(data['products']))




if __name__ == '__main__':
    main()
