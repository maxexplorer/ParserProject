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

# Функция получения id категорий
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


# Функция получения id товаров
def get_id_products(file_path: str, headers: dict) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        id_categories_list = [line.strip() for line in file.readlines()]

    count_categories = len(id_categories_list)

    print(f'Всего: {count_categories} категорий!')

    id_products_list = []
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

            print(f'Обработано: {i}/{count_categories}, получено {len(product_ids)} id товаров!')

    return id_products_list


# Функция получения json данных товаров
def get_products_array(id_products_list: list, headers: dict) -> None:
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     id_products_list = json.load(file)

    for item_dict in id_products_list:
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


# Функция получения данных товаров
def get_products_data(products_data: dict) -> None:

    result_data = []

    for item in products_data['products']:

        try:
            name = item['nameEn']
        except Exception:
            name = None

        if not name:
            continue

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        except Exception:
            price = 0

        try:
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            sizes_eur = ';'.join(item['name'] for item in sizes_items if item['visibilityValue'] == 'SHOW')
        except Exception:
            sizes_eur = None

        try:
            sizes_values = any(map(lambda value: value.isdigit(), sizes_eur.split(';')))
            if sizes_values:
                sizes_rus = sizes_eur
            else:
                sizes_rus = sizes_format(sizes=sizes_eur)
        except Exception:
            sizes_rus = None

        result_data.append(
            {
                '№': None,
                'Артикул': id_product,
                'Название товара': translator(name),
                'Цена, руб.*': round(price * rub),
                'Цена до скидки, руб.': None,
                'НДС, %*': None,
                'Включить продвижение': None,
                'Ozon ID': id_product,
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
                'Объединить на одной карточке*': sku,
                'Цвет товара*': color_ru,
                'Российский размер*': sizes_rus,
                'Размер производителя': sizes_eur,
                'Название цвета': color_en,
                'Тип*': translator(type_product),
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
                'Аннотация': translator(description),
                'Инструкция по уходу': translator(care),
                'Серия в одежде и обуви': None,
                'Материал': translator(material),
                'Состав материала': translator(composition),
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

    save_excel(data=result_data)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('data/result_list.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name='ОЗОН', index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    # id_categories_list = get_id_categories(headers=headers)
    id_products_list = get_id_products(file_path='data/id_categories_list.txt', headers=headers)
    get_products_array(id_products_list=id_products_list, headers=headers)


    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')



if __name__ == '__main__':
    main()
