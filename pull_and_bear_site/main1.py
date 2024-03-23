import os
import time
from datetime import datetime
import json

import requests
from requests import Session

from pandas import DataFrame, ExcelWriter
import openpyxl

from config import headers, params
from functions import colors_format
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')


# Функция получения id товаров
def get_id_products(id_categories_list_path: str, id_products_list_path: str, headers: dict) -> list[dict]:
    with open(id_categories_list_path, 'r', encoding='utf-8') as file:
        id_categories_list = [line.strip() for line in file.readlines()]

    with open(id_products_list_path, 'r', encoding='utf-8') as file:
        id_products_list = [line.strip() for line in file.readlines()]

    count_categories = len(id_categories_list)

    print(f'Всего: {count_categories} категорий!')

    new_id_list = []

    with Session() as session:
        for i, id_category in enumerate(id_categories_list[1:2], 1):
            time.sleep(3)

            try:
                response = session.get(
                    f'https://www.pullandbear.com/itxrest/3/catalog/store/24009400/20309422/category/{id_category}/product',
                    params=params,
                    headers=headers,
                )

                json_data = response.json()

                if response.status_code != 200:
                    print(f'id_category: {id_category} status_code: {response.status_code}')
                    continue

                json_data = response.json()

            except Exception as ex:
                print(f'get_id_products: {ex}')

            product_ids = json_data.get('productIds')

            for id_product in product_ids:
                if id_product in id_products_list:
                    continue

                new_id_list.append(id_product)

            print(f'Обработано: {i}/{count_categories}, получено {len(product_ids)} id товаров!')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
        print(*new_id_list, file=file, sep='\n')

    return new_id_list

# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict) -> None:
    for item_dict in products_data_list:
        for key in item_dict:
            lst = item_dict[key]
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

                print(f'Сбор данных id категории: {key}')
                get_products_data(products_data=json_data)

            except Exception as ex:
                print(f'get_products_array: {ex}')

# Функция получения json данных товаров
def get_new_products_array(id_products_list: list, headers: dict) -> None:

    params = {
        'languageId': '-1',
        'productIds': id_products_list,
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

        print(f'Сбор данных!')
        get_size_data(products_data=json_data)

    except Exception as ex:
        print(f'get_products_array: {ex}')


# Функция получения данных товаров
def get_products_data(products_data: dict) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name = item['nameEn']
            name = translator(name)
        except Exception:
            name = None

        if not name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
            old_price = round(old_price * rub)
        except Exception:
            old_price = 0

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_en = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = colors_format(value=color_en)

        except Exception:
            color_en = None
            color_ru = None

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
            for i in range(2, 11):
                additional_image = f"https://static.pullandbear.net/2/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_{i}_8.jpg"
                additional_images_list.append(additional_image)
            additional_images = '; '.join(additional_images_list)
        except Exception:
            additional_images = None

        # try:
        #     additional_images_list = []
        #     images_items = item['bundleProductSummaries'][0]['detail']['xmedia']
        #     for img_item in images_items:
        #         color_code = img_item['colorCode']
        #         if color_code == id_color:
        #             for img in img_item['xmediaItems'][0]['medias']:
        #                 additional_images_list.append(f"https://static.pullandbear.net/2/photos/{img['extraInfo']['url'].split('?')[0]}")
        #     additional_images = '; '.join(additional_images_list)
        #
        # except Exception:
        #     additional_images = None

        try:
            type_product = item['subFamilyNameEN']
            type_product = translator(type_product)
        except Exception:
            type_product = None

        try:
            gender_en = item['sectionNameEN']
            if gender_en == 'WOMEN':
                gender = 'женский'
            elif gender_en == 'MAN':
                gender = 'мужской'
            else:
                gender = gender_en
        except Exception:
            gender_en = None
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
            description = translator(description)
        except Exception:
            description = None

        try:
            care_items = item['bundleProductSummaries'][0]['detail']['care']
            care = ', '.join(item['description'] for item in care_items)
            care = translator(care)
        except Exception:
            care = None

        try:
            # composition = ''
            composition_items = item['bundleProductSummaries'][0]['detail']['composition']
            material = composition_items[0]['composition'][0]['name']
            material = translator(material)
            # for item in composition_items:
            #     for elem in item['composition']:
            #         composition += f"{elem['name']}: {elem['description']} "
            # is equivalent to
            composition = ' '.join(
                f"{elem['name']}: {elem['description']}" for item in composition_items for elem in item['composition'])
            composition = translator(composition)
        except Exception:
            composition = None
            material = None

        brand = 'Pull and Bear'

        try:
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            for item in sizes_items:
                size_sku = item.get('sku')
                size_eur = item.get('name')
                status_size = item.get('visibilityValue')
                if not size_eur.isdigit() and gender_en:
                    size_rus = sizes_format(gender=gender_en, size_eur=size_eur)
                else:
                    size_rus = size_eur

                result_data.append(
                    {
                        '№': None,
                        'Артикул': size_sku,
                        'Название товара': name,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': old_price,
                        'НДС, %*': None,
                        'Включить продвижение': None,
                        'Ozon ID': size_sku,
                        'Штрихкод (Серийный номер / EAN)': None,
                        'Вес в упаковке, г*': None,
                        'Ширина упаковки, мм*': None,
                        'Высота упаковки, мм*': None,
                        'Длина упаковки, мм*': None,
                        'Ссылка на главное фото*': main_image,
                        'Ссылки на дополнительные фото': additional_images,
                        'Ссылки на фото 360': None,
                        'Артикул фото': None,
                        'Бренд в одежде и обуви*': brand,
                        'Объединить на одной карточке*': reference,
                        'Цвет товара*': color_ru,
                        'Российский размер*': size_rus,
                        'Размер производителя': size_eur,
                        'Статус наличия': status_size,
                        'Название цвета': color_en,
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
                        'Материал': material,
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
        except Exception as ex:
            print(f'sizes: {ex}')

    save_excel(data=result_data, flag='products')


# Функция получения данных размеров товаров
def get_size_data(products_data: dict) -> None:
    result_data = []

    for item in products_data['products']:
        # try:
        #     id_product = item['id']
        # except Exception:
        #     id_product = None
        #
        # try:
        #     reference = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0]
        # except Exception:
        #     reference = None

        try:
            name = item['nameEn']
            name = translator(name)
        except Exception:
            name = None

        if not name:
            continue

        # try:
        #     old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
        #     old_price = round(old_price * rub)
        # except Exception:
        #     old_price = 0

        # try:
        #     price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        #     price = round(price * rub)
        # except Exception:
        #     price = 0

        try:
            size = ''
            status_dict = {}
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            for item in sizes_items:
                size_sku = item.get('sku')
                size_eur = item.get('name')
                status_size = item.get('visibilityValue')
                if size == size_eur:
                    if status_size in status_dict.get(size_eur):
                        continue
                status_dict.setdefault(size_eur, []).append(status_size)
                size = size_eur

                result_data.append(
                    {
                        'Артикул': size_sku,
                        'Статус наличия': status_size,
                    }
                )
        except Exception as ex:
            print(f'sizes: {ex}')

    save_excel(data=result_data, flag='size')


# Функция для записи данных в формат xlsx
def save_excel(data: list, flag: str) -> None:
    if not os.path.exists('data'):
        os.makedirs('data')

    dataframe = DataFrame(data)

    with ExcelWriter(f'data/result_{flag}_data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='ОЗОН', index=False)

    print(f'Данные сохранены в файл "result_{flag}_data.xlsx"')


def main():
    new_id_list = get_id_products(id_categories_list_path='data/id_categories_list.txt',
                                       id_products_list_path='data/id_products_list.txt', headers=headers)
    if new_id_list:
        get_new_products_array(id_products_list=new_id_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
