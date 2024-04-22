import os
import time
from datetime import datetime

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_categories_list_rus
from data.data import id_categories_list_baby

from data.data import id_region_dict
# from data.data import products_data_list

from functions import colors_format_ru
from functions import colors_format_en
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()

base_currency = 'EUR'
# base_currency = 'KZT'
target_currency = 'RUB'

rub = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)

print(f'Курс EUR/RUB: {rub}')
# print(f'Курс KZT/RUB: {rub}')

result_data = []


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> list[dict]:
    with open('data/id_products_list.txt', 'r', encoding='utf-8') as file:
        id_products_list = [line.strip() for line in file.readlines()]

    products_data_list = []
    products_new_data_list = []

    with Session() as session:
        for category_dict in id_categories_list:
            new_id_list = []
            for main_category, products_list in category_dict.items():
                for product_tuple in products_list:
                    product_ids = []
                    name_category, id_category = product_tuple

                    time.sleep(1)

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
                        continue

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

                                    # if str(id_product) in id_products_list:
                                    #     continue
                                    # new_id_list.append(id_product)

                    except Exception as ex:
                        print(f'id_poducts: {ex}')

                    products_data_list.append(
                        {
                            (main_category, name_category, id_category): product_ids
                        }
                    )

                    # if new_id_list:
                    #     products_new_data_list.append(
                    #         {
                    #             (name_category, id_category): new_id_list
                    #         }
                    #     )

                    print(
                        f'Обработано: категория {main_category}/{name_category}/{id_category} - {len(product_ids)} товаров!')

    # if not os.path.exists('data'):
    #     os.makedirs('data')
    #
    # with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
    #     print(*new_id_list, file=file, sep='\n')

    return products_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str) -> None:
    global result_data

    processed_ids = []

    with Session() as session:
        for dict_item in products_data_list:
            count = 0
            id_products = []
            key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

            for id_product in values:
                if id_product not in processed_ids:
                    processed_ids.append(id_product)
                    id_products.append(id_product)
            main_category = key[0]
            type_product = key[1]

            print(f'Сбор данных о наличии размеров в категории {key[0]}/{key[1]}/{key[2]}')

            for chunk_ids in chunks(id_products, 10):
                params = {
                    'productIds': chunk_ids,
                    'ajax': 'true',
                }

                try:
                    time.sleep(1)
                    response = session.get(
                        f'https://www.zara.com/{id_region}/products-details',
                        params=params,
                        headers=headers,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')
                        continue

                    json_data = response.json()

                    result_data = get_size_data(products_data=json_data, main_category=main_category,
                                                type_product=type_product)
                    count += len(chunk_ids)

                    print(f'Обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue

            save_excel(data=result_data)

            result_data = []


# Функция получения данных товаров
def get_size_data(products_data: dict, main_category: str, type_product: str) -> list:
    for item in products_data:
        try:
            id_product = item['detail']['colors'][0]['productId']
        except Exception:
            id_product = None

        try:
            reference = item['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name_product = item['name']
            name_product = f'ZARA {translator(name_product)}'
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_original = item['detail']['colors'][0]['name']
            color_ru = colors_format_en(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            sizes_items = item['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                status_size = size_item.get('availability')

                if main_category == 'Девочки' or main_category == 'Мальчики' or main_category == 'Девочки;Мальчики':
                    try:
                        size_rus = ''.join(i for i in size_eur.split()[-2] if i.isdigit())
                    except Exception:
                        size_rus = size_eur

                    if not size_rus:
                        size_rus = size_eur

                    if color_original is not None:
                        id_product_size = f"{reference}/{color_original.replace(' ', '-')}/{size_rus}"
                    else:
                        id_product_size = None

                else:
                    if color_original is not None:
                        id_product_size = f"{id_product}/{color_original.replace(' ', '-')}/{size_eur}/{reference}"
                    else:
                        id_product_size = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Цена': price,
                        'Статус наличия': status_size,
                    }
                )
        except Exception as ex:
            print(f'sizes: {ex}')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/result_data_zara_size.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/result_data_zara_size.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel('results/result_data_zara_size.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter('results/result_data_zara_size.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data_size.xlsx"')


def main():
    region = 'Германия'
    id_region = id_region_dict.get(region)
    products_data_list = get_id_products(id_categories_list=id_categories_list_rus,
                                         headers=headers, params=params,
                                         id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
