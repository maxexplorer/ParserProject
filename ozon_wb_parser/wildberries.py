import json
import os.path
import time
from datetime import datetime
from random import randint
from math import floor

from requests import Session

from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

# Функция для получения id бренда
def get_id_brand(url: str, session: Session) -> int:
    headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': url,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    brand = url.split('brands')[-1].strip()

    try:
        time.sleep(randint(1, 3))
        response = session.get(f'https://static-basket-01.wbbasket.ru/vol0/data/brands{brand}.json', headers=headers,
                               timeout=30)

        if response.status_code != 200:
            print(f'id_brand: {url} status_code: {response.status_code}')

        json_data = response.json()

        id_brand = json_data.get('id')
    except Exception as ex:
        print(f'{url}: {ex}')
        id_brand = None

    return id_brand

# Функция для получения данных о продукте
def get_data_products(file_path: str):
    # Открываем файл в формате .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    result_list = []

    # Создаем сессию
    with Session() as session:
        for url in urls_list:

            print(f'Обрабатывается: {url}')

            time.sleep(randint(1, 3))

            # Получаем id продавца
            id_brand = get_id_brand(url=url, session=session)

            if id_brand is None:
                continue

            headers = {
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Origin': 'https://www.wildberries.ru',
                'Referer': url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'appType': '1',
                'brand': id_brand,
                'curr': 'rub',
                'dest': '-1257786',
                'sort': 'popular',
                'spp': '30',
            }

            try:
                time.sleep(randint(1, 3))
                response = session.get('https://catalog.wb.ru/brands/b/catalog', params=params, headers=headers,
                                       timeout=30)

                if response.status_code != 200:
                    print(f'catalog: {url} status_code: {response.status_code}')
                    continue
            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            try:
                json_data = response.json()
                prod_items = json_data['data']['products']
                count_prod = len(prod_items)
            except Exception as ex:
                print(f'json_data: {url} - {ex}')
                continue

            for i, item in enumerate(prod_items, 1):
                # Название бренда
                brand = item.get('brand')

                # Название товара
                name = item.get('name')

                # Артикул продукта
                id_product = item.get('id')

                # Цвета продукта
                # colors = ', '.join(c.get('name') for c in item.get('colors'))

                colors = get_card_product(id_product=id_product, session=session)

                # Ценна со скидкой
                sale_price = item.get('salePriceU', 0) // 100

                # Рейтинг
                reviewRating = item.get('reviewRating')

                # Количество отзывов
                count_feedbacks = item['feedbacks']

                # Цена с WB кошельком
                wb_price = floor(sale_price * 0.95)

                # imt_id необходим для формирования ссылки и получения данных feedbacks
                imt_id = item.get('root')

                if imt_id:
                    try:
                        average_rating = get_feedbacks(imt_id=imt_id, session=session)
                    except Exception:
                        average_rating = None

                url_product = f"https://www.wildberries.ru/catalog/{id_product}/detail.aspx"

                result_list.append(
                    {
                        'Wildberries': 'Wildberries',
                        'Ссылка': url_product,
                        'Бренд': brand,
                        'Название': name,
                        'SKU': id_product,
                        'Цвет': colors,
                        'РЦ+СПП': sale_price,
                        'Рейтинг': reviewRating,
                        'Кол-во отзывов': count_feedbacks,
                        'Последние 5 отзывов': average_rating,
                        'Цена с WB кошельком': wb_price
                    }
                )

                print(f'Обработано: {i}/{count_prod}')

    return result_list

# Функция для получения данных о цветах из карточки продукта
def get_card_product(id_product: int, session: Session) -> str:
    short_id = id_product // 100000

    match short_id:
        case int(short_id) if 0 <= short_id <= 143:
            basket = '01'
        case int(short_id) if 144 <= short_id <= 287:
            basket = '02'
        case int(short_id) if 288 <= short_id <= 431:
            basket = '03'
        case int(short_id) if 432 <= short_id <= 719:
            basket = '04'
        case int(short_id) if 720 <= short_id <= 1007:
            basket = '05'
        case int(short_id) if 1008 <= short_id <= 1061:
            basket = '06'
        case int(short_id) if 1062 <= short_id <= 1115:
            basket = '07'
        case int(short_id) if 1116 <= short_id <= 1169:
            basket = '08'
        case int(short_id) if 1170 <= short_id <= 1313:
            basket = '09'
        case int(short_id) if 1314 <= short_id <= 1601:
            basket = '10'
        case int(short_id) if 1602 <= short_id <= 1655:
            basket = '11'
        case int(short_id) if 1656 <= short_id <= 1919:
            basket = '12'
        case int(short_id) if 1920 <= short_id <= 2045:
            basket = '13'
        case int(short_id) if 2046 <= short_id <= 2189:
            basket = '14'
        case int(short_id) if short_id > 2189:
            basket = '15'
        case _:
            print('Значение должно быть class int')
            basket = None

    headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': f'https://www.wildberries.ru/catalog/{id_product}/detail.aspx',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        response = session.get(
            f'https://basket-{basket}.wbbasket.ru/vol{short_id}/part{id_product // 1000}/{id_product}/info/ru/card.json',
            headers=headers)
        if response.status_code != 200:
            print(f'colors: {id_product} status_code: {response.status_code}')

        json_data = response.json()

        colors = json_data['nm_colors_names']

    except Exception as ex:
        print(f'{id_product}: {ex}')
        colors = None

    return colors

# Функция для получения отзывов о продукте
def get_feedbacks(imt_id: int, session: Session) -> int:
    try:
        time.sleep(randint(1, 2))
        response = session.get(f'https://feedbacks1.wb.ru/feedbacks/v1/{imt_id}')

        if response.status_code != 200:
            print(f'feedbacks: {imt_id} status_code: {response.status_code}')

        json_data = response.json()

        json_data = json_data.get('feedbacks')

    except Exception as ex:
        print(f'{imt_id}: {ex}')
        json_data = None

    if json_data:
        # Сортировка списка словарей по дате
        # sorted_list_of_dicts = sorted([i for i in json_data], key=extract_date, reverse=True)
        sorted_list_of_dicts = sorted([item for item in json_data],
                                      key=lambda item: datetime.strptime(item['createdDate'], "%Y-%m-%dT%H:%M:%SZ"),
                                      reverse=True)

        # Вычисляем среднюю оценку последних 5 отзывов
        # Если количество отзывов меньше 5
        if len(json_data['feedbacks']) < 5:
            average_rating = sum(item['productValuation'] for item in sorted_list_of_dicts[:5]) / len(json_data['feedbacks'])
            return average_rating
        average_rating = sum(item['productValuation'] for item in sorted_list_of_dicts[:5]) / 5

        return average_rating


# Функция для извлечения даты из строки и преобразования в объект datetime
def extract_date(dict_item):
    return datetime.strptime(dict_item['createdDate'], "%Y-%m-%dT%H:%M:%SZ")

# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('data'):
        os.makedirs('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list_1.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='WB', index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    result_data = get_data_products(file_path='data/urls_list.txt')
    save_excel(data=result_data)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
