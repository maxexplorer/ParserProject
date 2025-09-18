import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math

from requests import Session
import pandas as pd
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import category_dict

start_time = datetime.now()


def get_products_data(category_dict: dict, batch_size: int = 50) -> None:
    """Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel"""
    with Session() as session:
        for category_name, category_url in category_dict.items():
            parsed_url = urlparse(category_url)
            params_qs = parse_qs(parsed_url.query)
            xsubject = params_qs.get("xsubject", [None])[0]

            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': category_url,
                'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            }

            # первый запрос для получения total
            first_params = {
                    'ab_testid': 'top_gmv',
                    'appType': '1',
                    'curr': 'rub',
                    'dest': '-1257786',
                    'lang': 'ru',
                    'page': 1,
                    'query': category_name,
                    'resultset': 'catalog',
                    'sort': 'popular',
                    'spp': '30',
                    'suppressSpellcheck': 'false',
                    # 'xsubject': xsubject,
                }

            try:
                time.sleep(1)
                response = session.get(
                    'https://u-search.wb.ru/exactmatch/ru/common/v18/search',
                    params=first_params,
                    headers=headers,
                    timeout=(3, 5)
                )
                response.raise_for_status()
                json_data: dict = response.json()
                total = json_data.get('total', 0)
                if total == 0:
                    print(f"{category_name}: товаров нет")
                    continue

                pages = math.ceil(total / batch_size)
                print(f"{category_name}: всего {total} товаров, {pages} страниц")

            except Exception as ex:
                print(f"{category_name}: ошибка получения total: {ex}")
                continue

            result_list = []

            # проходим по всем страницам
            for page in range(1, pages + 1):
                params = first_params.copy()
                params['page'] = page

                try:
                    time.sleep(1)
                    response = session.get(
                        'https://u-search.wb.ru/exactmatch/ru/common/v18/search',
                        params=params,
                        headers=headers,
                        timeout=(3, 5)
                    )
                    response.raise_for_status()
                    json_data = response.json()
                    data: list = json_data.get('products', [])

                except Exception as ex:
                    print(f"{category_name} страница {page}: {ex}")
                    continue


                if not data:
                    continue

                for item in data:
                    item: dict

                    brand = item.get('brand')

                    name = item.get('name')

                    size = item.get('sizes', [])[0].get('origName')

                    price = item.get('sizes', [])[0].get('price', {}).get('product')

                    result_list.append(
                        {
                            'Бренд': brand,
                            'Название': name,
                            'Размер': size,
                            'Цена': price,
                        }
                    )

            # Загружаем в DataFrame
            df = pd.DataFrame(result_list)

            # Группируем по бренду и товару, считаем min, max, median
            result = df.groupby(["brand", "product"])["price"].agg(
                min_price="min",
                max_price="max",
                median_price="median"
            ).reset_index()

            save_excel(result)

            print(f"{category_name}: данные сохранены, {len(result)} записей")


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    df_existing = read_excel(file_path, sheet_name='Sellers')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Sellers', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main() -> None:
    """
    Точка входа в программу. Запускает обработку продавцов в заданном диапазоне.
    """

    get_products_data(category_dict=category_dict)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
