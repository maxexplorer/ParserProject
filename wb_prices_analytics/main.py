import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from requests import Session
import pandas as pd
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import category_dict

start_time = datetime.now()


def get_products_data(category_dict: dict, batch_size: int = 50) -> None:
    result_list = []

    with Session() as session:
        for category_name, category_url in category_dict.items():
            parsed_url = urlparse(category_url)
            params = parse_qs(parsed_url.query)
            xsubject = params.get("xsubject", [None])[0]

            pages = 1

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
                'x-pow': '2|site_b19c142c268d48699680efbe9d1e554d|1758179724|8,8,1,28f5c28f5c28f5c,33b9a1e5-9937-4d2e-ab50-3ee3df6f79c1,2df9be27-b150-4999-9532-07863bdc5111,1758179904,1,wl5rj6YOWxUvudkPaMx1Veh+SFaQObu2LHsv/0OSScI=,03999862c2979815cb43b21597488e92b66c525ef513b45a2e15323cbbe9c01a19195f34d7764cef86af8f16ef301777c3f08ffdac8e4e2bf3b401ee21833b0e|104',
                'x-queryid': 'qid143023290172907954520250918075200',
                'x-userid': '0',
            }

            for page in range(1, pages + 1):
                params = {
                    'ab_testid': 'top_gmv',
                    'appType': '1',
                    'curr': 'rub',
                    'dest': '-1257786',
                    'lang': 'ru',
                    'page': page,
                    'query': category_name,
                    'resultset': 'catalog',
                    'sort': 'popular',
                    'spp': '30',
                    'suppressSpellcheck': 'false',
                    # 'xsubject': xsubject,
                }

                try:
                    response = session.get(
                        'https://u-search.wb.ru/exactmatch/ru/common/v18/search',
                        params=params,
                        headers=headers,
                        timeout=(3, 5)
                    )

                    if response.status_code != 200:
                        print(f' category_url: {category_url}: статус ответа {response.status_code}')
                        continue

                    json_data: dict = response.json()
                    data: list = json_data.get('products', [])

                except Exception as ex:
                    print(f'{category_url}: {ex}')
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
