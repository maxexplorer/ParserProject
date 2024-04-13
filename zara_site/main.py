import os
import time
from datetime import datetime
from random import randint
import json

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_categories_list
from data.data import id_region_dict
from data.data import products_data_list
# from functions import colors_format
# from functions import sizes_format
from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')


# Функция получения id категорий
def get_id_categories(headers: dict, params: dict) -> None:
    id_categories_data = []

    with Session() as session:
        try:
            response = session.get(
                'https://www.zara.com/kz/ru/categories',
                headers=headers,
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                print(f'status_code: {response.status_code}')

            json_data = response.json()
        except Exception as ex:
            print(f'get_id_categories: {ex}')

    try:
        category_items = json_data['categories']
    except Exception:
        category_items = []

    for category_item in category_items[:3]:
        category_name = category_item.get('sectionName')
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            subcategory_name = subcategory_item.get('name')
            subcategory_id = subcategory_item.get('id')
            redirect_category_id = subcategory_item.get('redirectCategoryId')
            category_id = redirect_category_id if redirect_category_id else subcategory_id
            id_categories_data.append((subcategory_name, category_id))
            # print(f"('{subcategory_name}', {category_id}),")
            if category_name == 'KID':
                subcategory_kid_items = subcategory_item.get('subcategories')
                for subcategory_kid_item in subcategory_kid_items:
                    subcategory_kid_name = subcategory_kid_item.get('name')
                    subcategory_kid_id = subcategory_kid_item.get('id')
                    redirect_category_kid_id = subcategory_kid_item.get('redirectCategoryId')
                    category_kid_id = redirect_category_kid_id if redirect_category_kid_id else subcategory_kid_id
                    id_categories_data.append((subcategory_kid_name, category_kid_id))

    with open('data/id_categories_list_rus.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_data, file=file, sep=',\n')


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> list[dict]:
    products_data_list = []
    id_products_list = []
    with Session() as session:
        for category_dict in id_categories_list:
            for category, products_list in category_dict.items():
                for product_tuple in products_list:
                    product_ids = []
                    name_category, id_category = product_tuple

                    time.sleep(randint(3, 5))

                    try:
                        response = session.get(
                            f'https://www.zara.com/{id_region}/category/{id_category}/products',
                            params=params,
                            headers=headers,
                            timeout=60
                        )

                        if response.status_code != 200:
                            print(f'id_category: {id_category} status_code: {response.status_code}')
                            continue

                        json_data = response.json()

                    except Exception as ex:
                        print(f'get_id_products: {ex}')

                    try:
                        product_data = json_data['productGroups']
                    except Exception:
                        product_ids = []

                    try:
                        for group_item in product_data:
                            elements = group_item['elements']
                            for element in elements:
                                try:
                                    commercial_components = element['commercialComponents']
                                except Exception:
                                    continue
                                for component in commercial_components:
                                    try:
                                        id_product = component['id']
                                    except Exception:
                                        id_product = None
                                    product_ids.append(id_product)
                                    id_products_list.append(id_product)
                    except Exception as ex:
                        print(f'id_poducts: {ex}')

                    products_data_list.append(
                        {
                            (name_category, id_category): product_ids
                        }
                    )

                    print(f'Обработано: категория {category}/{name_category}/{id_category} - {len(product_ids)} товаров!')


    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
        print(*id_products_list, file=file, sep='\n')

    return products_data_list

# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str) -> None:
    with Session() as session:
        for item_dict in products_data_list:
            for key in item_dict:
                type_product = key[0]
                id_products = item_dict[key][:10]

                params = {
                    'productIds': id_products,
                    'ajax': 'true',
                }

                try:
                    response = session.get(
                        f'https://www.zara.com/kz/ru/products-details',
                        params=params,
                        headers=headers,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')

                    json_data = response.json()

                    with open('data/json_data.json', 'w', encoding='utf-8') as file:
                        json.dump(json_data, file, indent=4, ensure_ascii=False)

                    # print(f'Сбор данных категории: {key[0]}/{key[1]}')
                    # get_products_data(products_data=json_data, type_product=type_product)

                except Exception as ex:
                    print(f'get_products_array: {ex}')


def main():
    region = 'Казахстан'
    id_region = id_region_dict.get(region)
    # get_id_categories(headers=headers, params=params)
    # get_id_products(id_categories_list=id_categories_list, headers=headers, params=params, id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region)




if __name__ == '__main__':
    main()
