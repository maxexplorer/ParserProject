import json
import os
import time
from datetime import datetime
from random import randint

import requests
from requests import Session
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter
import openpyxl

from config import headers, params

start_time = datetime.now()


def get_id_categories(headers: dict) -> list:
    id_categories_list = []

    with Session() as session:
        try:
            response = session.get(
                'https://www.pullandbear.com/itxrest/2/catalog/store/24009400/20309422/category',
                params=params,
                headers=headers,
            )

            if response.status_code != 200:
                print(f'status_code: {response.status_code}')

            json_data = response.json()
        except Exception as ex:
            print(f'get_id_categories: {ex}')

    category_items = json_data['categories']

    for category_item in category_items[:2]:
        category_name = category_item.get('name')
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            if subcategory_item.get('name') == 'Clothing':
                clothing_subcategory_items = subcategory_item.get('subcategories')
                for clothing_subcategory_item in clothing_subcategory_items:
                    id_category = clothing_subcategory_item.get('id')
                    subcategory_name = clothing_subcategory_item.get('name')
                    if subcategory_name == '-':
                        continue
                    if 'Best sellers' in subcategory_name:
                        break
                    subcategories = clothing_subcategory_item.get('subcategories')
                    if subcategories:
                        for subcategory in subcategories:
                            if subcategory_name == 'Jeans' and subcategory.get('name') == 'See all':
                                id_category = subcategory.get('id')
                                id_categories_list.append(id_category)
                            else:
                                id_categories_list.append(id_category)
                    else:
                        id_categories_list.append(id_category)

                    print(category_name, subcategory_name)

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_categories_list.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_list, file=file, sep='\n')

    return id_categories_list


def get_id_products(file_path: str, headers: dict) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        id_categories_list = [line.strip() for line in file.readlines()]

    count_categories = len(id_categories_list)

    print(f'Всего: {count_categories} категорий!')

    id_products_list = []
    with Session() as session:
        for i, id_category in enumerate(id_categories_list, 1):
            time.sleep(1)

            try:
                response = session.get(
                    f'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/category/{id_category}/product',
                    params=params,
                    headers=headers,
                )

                json_data = response.json()

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')

                json_data = response.json()

            except Exception as ex:
                print(f'get_id_products: {ex}')

            product_ids = json_data.get('productIds')

            id_products_list.append(
                {
                    id_category: product_ids
                }
            )

            print(f'Обработано: {i}/{count_categories}')

    # if not os.path.exists('data'):
    #     os.makedirs('data')

    # with open('data/id_products_list.json', 'w', encoding='utf-8') as file:
    #     json.dump(id_products_list, file, indent=4, ensure_ascii=False)

    return id_products_list


def get_products_array(file_path: str, headers: dict) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        id_products_list = json.load(file)

    for item_dict in id_products_list[1:2]:
        for key in item_dict:
            lst = item_dict[key][:10]
            id_products = ','.join(map(str, lst))

            params = {
                'languageId': '-1',
                'productIds': id_products,
                'categoryId': key,
                'appId': '1',
            }

            try:
                response = requests.get(
                    'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/productsArray',
                    params=params,
                    headers=headers,
                )

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')

                json_data = response.json()

                return json_data

            except Exception as ex:
                print(f'get_products_array: {ex}')
            #
            # if not os.path.exists('data'):
            #     os.makedirs('data')
            #
            # with open('data/products_array1.json', 'w', encoding='utf-8') as file:
            #     json.dump(response.json(), file, indent=4, ensure_ascii=False)


def get_data(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        products_data = json.load(file)

    result_data = []

    for item in products_data['products'][:1]:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            sku = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0]
        except Exception:
            sku = None

        try:
            name = item['nameEn']
        except Exception:
            name = None

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        except Exception:
            price = None

        try:
            color = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']

        except Exception:
            color = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            main_image = f"https://static.pullandbear.net/2/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_1_8.jpg"
        except Exception:
            main_image = None

        try:
            additional_images_list = []
            images_items = item['bundleProductSummaries'][0]['detail']['xmedia']
            for img_item in images_items:
                color_code = img_item['colorCode']
                if color_code == id_color:
                    for img in img_item['xmediaItems'][0]['medias']:
                        additional_images_list.append(f"https://static.pullandbear.net/2/photos/{img['extraInfo']['url'].split('?')[0]}")
            additional_images = '; '.join(additional_images_list)

        except Exception:
            additional_images = None

        try:
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            sizes = ';'.join(item['name'] for item in sizes_items if item['visibilityValue'] == 'SHOW')
        except Exception:
            sizes = None

        try:
            type_product = item['subFamilyNameEN']
        except Exception:
            type_product = None

        try:
            gender = item['sectionNameEN']
        except Exception:
            gender = None

        try:
            model_height = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelHeigh']
        except Exception:
            model_height = None

        try:
            model_size = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelSize']
        except Exception:
            model_size = None

        try:
            description = item['detail']['longDescription']
        except Exception:
            description = None

        try:
            care_items = item['bundleProductSummaries'][0]['detail']['care']
            care = ', '.join(item['description'] for item in care_items)
        except Exception:
            care = None

        try:
            # composition = ''
            composition_items = item['bundleProductSummaries'][0]['detail']['composition']
            # for item in composition_items:
            #     for elem in item['composition']:
            #         composition += f"{elem['name']}: {elem['description']} "

            composition = ' '.join(
                f"{elem['name']}: {elem['description']}" for item in composition_items for elem in item['composition'])

        except Exception:
            composition = None


        brand = 'Pull and Bear'

        result_data.append(
            {
                '№': None,
                'Артикул': id_product,
                'Название товара': name,
                'Цена, руб.*': price,
                'Цена до скидки, руб.': None,
                'НДС, %*': None,
                'Включить продвижение': None,
                'Ozon ID': id_product,
                'Штрихкод (Серийный номер / EAN)': None,
                'Вес в упаковке, г*': None,
                'Ширина упаковки, мм*': None,
                'Высота упаковки, мм*': None,
                'Длина упаковки, мм*': None,
                'Ссылка на главное фото*': None,
                'Ссылки на дополнительные фото': None,
                'Ссылки на фото 360': None,
                'Артикул фото': None,
                'Бренд в одежде и обуви*': brand,
                'Объединить на одной карточке*': sku,
                'Цвет товара*': color,
                'Российский размер*': None,
                'Размер производителя': sizes,
                'Название цвета': color,
                'Тип*': type_product,
                'Пол*': gender,
                'Размер пеленки': None,
                'ТН ВЭД коды ЕАЭС': None,
                'Ключевые слова': None,
                'Сезон': None,
                'Рост модели на фото': model_height,
                'Параметры модели на фото': None,
                'Размер товара на фото': model_size,
                'Коллекция': None,
                'Страна-изготовитель': None,
                'Вид принта': None,
                'Аннотация': description,
                'Инструкция по уходу': care,
                'Серия в одежде и обуви': None,
                'Материал': composition,
                'Состав материала': composition,
                'Материал подклада/внутренней отделки': None,
                'Материал наполнителя': None,
                'Утеплитель, гр': None,
                'Диапазон температур, °С': None,
                'Стиль': None,
                'Вид спорта': None,
                'Вид одежды': None,
                'Тип застежки': None,
                'Длина рукава': None,
                'Талия': None,
                'Для беременных или новорожденных': None,
                'Тип упаковки одежды': None,
                'Количество в упаковке': None,
                'Состав комплекта': None,
                'Рост': None,
                'Длина изделия, см': None,
                'Длина подола': None,
                'Форма воротника/горловины': None,
                'Детали': None,
                'Таблица размеров JSON': None,
                'Rich-контент JSON': None,
                'Плотность, DEN': None,
                'Количество пар в упаковке': None,
                'Класс компрессии': None,
                'Персонаж': None,
                'Праздник': None,
                'Тематика карнавальных костюмов': None,
                'Признак 18+': None,
                'Назначение спецодежды': None,
                'HS-код': None,
                'Количество заводских упаковок': None,
                'Ошибка': None,
                'Предупреждение': None,
            }
        )

# Функция для записи данных в формат xlsx
def save_excel_wb(data: list) -> None:
    if not os.path.exists('data/result_list.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='WB', index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name='WB', index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    # id_categories_list = get_id_categories(headers=headers)
    # id_products_list = get_id_products(file_path='data/id_categories_list.txt', headers=headers)
    # products_data = get_products_array(file_path='data/id_products_list.json', headers=headers)
    result_data = get_data(file_path='data/products_array1.json')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')

    # with open('data/products_array1.json') as file:
    #     data = json.load(file)
    #
    # print(len(data['products']))


if __name__ == '__main__':
    main()
