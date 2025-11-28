import os
import time
from datetime import datetime
import json

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

from configs.config import headers, cookies
from data.data import category_data

# Засекаем время работы программы
start_time = datetime.now()


def get_product_ids(categories_data: list, headers: dict, cookies: dict) -> None:
    """
    Собирает все product IDs для каждой категории с учётом пагинации.

    :param categories_data: список кортежей (main_category_name, category_name, category_id)
    :param headers: HTTP заголовки
    :param cookies: cookies
    :return: список всех product_ids
    """

    with Session() as session:
        for category_data in categories_data:
            main_category_name, category_name, category_id = category_data
            print(f'Обработка категории: {category_name}')

            offset = 0
            limit = 72
            total = None
            processed_count = 0

            while True:
                params = {
                    'categoryIds': category_id,
                    'offset': str(offset),
                    'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiLTEyIiwiZGEiXQ==',
                    'limit': str(limit),
                    'doTranslit': 'true',
                    'context': 'v2dzaG9wX2lkZFMwMDJsY2F0ZWdvcnlfaWRzn2M0MDD/ZmNhdF9JZGM0MDD/',
                }

                try:
                    response = session.get(
                        'https://www.mvideo.ru/bff/products/v2/search',
                        headers=headers,
                        cookies=cookies,
                        params=params,
                    )
                    response.raise_for_status()
                    json_data = response.json()
                except Exception as ex:
                    print(f'get_product_ids: {ex}')

                product_ids = json_data.get('body', {}).get('products')

                # Инициализируем total при первом запросе
                if total is None:
                    total = json_data['body'].get('total', 0)

                get_product_data(product_ids=product_ids, session=session, headers=headers, cookies=cookies,
                                 main_category_name=main_category_name, category_name=category_name)

                # Обновляем прогресс
                processed_count += len(product_ids)
                print(f"Прогресс категории '{category_name}': {processed_count}/{total}", end='\r')

                offset += limit
                if offset >= total:
                    print(f'Обработана категория: {category_name}')
                    break


def get_product_prices(product_ids: list[str], session: Session, headers: dict, cookies: dict) -> dict:
    """
    Загружает цены для списка product_ids и возвращает словарь:
    {productId: {'Цена': base_price, 'Цена со скидкой': sale_price}}

    :param product_ids: список ID товаров
    :param session: requests.Session
    :param headers: словарь HTTP-заголовков
    :param cookies: cookies
    :return: словарь с ценами
    """
    price_data = {}

    # Передаём product_ids как строку через запятую
    product_ids_str = ','.join(product_ids)

    params = {
        'productIds': product_ids_str,
        'addBonusRubles': 'true',
        'isPromoApplied': 'true',
    }

    try:
        response = session.get(
            'https://www.mvideo.ru/bff/products/prices',
            headers=headers,
            cookies=cookies,
            params=params,
        )
        response.raise_for_status()
        json_data = response.json()
    except Exception as ex:
        print(f'get_product_prices: {ex}')
        return price_data  # возвращаем пустой словарь при ошибке

    price_items = json_data.get('body', {}).get('materialPrices', [])

    if not price_items:
        print('No price items found')

    for price_item in price_items:
        product_id = price_item.get('productId')
        base_price = price_item.get('price', {}).get('basePrice')
        sale_price = price_item.get('price', {}).get('salePrice')

        price_data[product_id] = {
            'Цена': base_price,
            'Цена со скидкой': sale_price
        }

    return price_data


def get_product_data(product_ids: list[str], session: Session, headers: dict, cookies: dict,
                     main_category_name: str, category_name: str):
    """
    Загружает данные о товарах с API сайта и сохраняет их партиями в Excel.

    :param product_ids: список ID товаров
    :param session: requests.Session
    :param headers: словарь HTTP-заголовков
    :param cookies: cookies
    :param main_category_name: основная категория
    :param category_name: подкатегория
    :return: None
    """
    result_data = []

    # Запрос данных о товарах
    json_data = {
        'productIds': product_ids,
        'mediaTypes': ['images'],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': ['KEY'],
        'propertiesConfig': {'propertiesPortionSize': 5},
    }

    try:
        response = session.post(
            'https://www.mvideo.ru/bff/product-details/list',
            headers=headers,
            cookies=cookies,
            json=json_data,
        )
        response.raise_for_status()
        product_items = response.json().get('body', {}).get('products', [])
    except Exception as ex:
        print(f'get_product_data: {ex}')
        return

    if not product_items:
        print('No product items')
        return

    # Получаем цены **одним запросом для всех product_ids**
    price_data = get_product_prices(product_ids=product_ids, session=session, headers=headers, cookies=cookies)

    for product_item in product_items:

        product_id = product_item.get('productId')
        brand = product_item.get('brandName')
        model = product_item.get('modelName')
        product_name = product_item.get('name', '').replace(model, '')

        # Атрибуты товара
        product_attributes = {
            'Основная категория': main_category_name,
            'Kатегория': category_name,
            'Товар': product_name,
            'Бренд': brand,
            'Модель': model
        }

        # Добавляем цены из price_map
        price_info = price_data.get(product_id, {})

        # Объединяем все данные
        result_dict = {**product_attributes, **price_info}

        # Параметры товара
        product_parameters = {}
        for prop_item in product_item.get('propertiesPortion', []):
            product_parameters[prop_item.get('name')] = prop_item.get('value')

        result_dict.update(product_parameters)

        result_data.append(result_dict)

    # Сохраняем в Excel
    save_excel(result_data)


def save_excel(data: list) -> None:
    """
    Сохраняет список товаров в Excel (results/result_data.xlsx).

    :param data: список словарей с данными о товарах
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1,
                        header=(num_existing_rows == 0),
                        sheet_name='Data', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main():
    """
    Основная функция программы.
    Собирает данные о товарах и сохраняет их в Excel.
    """

    get_product_ids(categories_data=category_data, headers=headers, cookies=cookies)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
