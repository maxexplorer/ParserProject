import os
import time
from datetime import datetime
from random import randint

from requests import Session

import pandas as pd
from pandas import DataFrame, ExcelWriter
from pandas import read_excel

start_time = datetime.now()


# Функция для получения данных о наличии товаров у продавца
def get_data_products_wb() -> None:
    result_list = []
    batch_size = 100
    # Размер пакета для записи
    processed_count = 0  # Счетчик обработанных URL

    # Создаем сессию
    with Session() as session:
        for i in range(1, 4_000_001):
            url = f"https://www.wildberries.ru/seller/{i}"
            # time.sleep(1)

            headers = {
                'Accept': '*/*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Origin': 'https://www.wildberries.ru',
                'Referer': url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-5551776',
                'sort': 'popular',
                'spp': '30',
                'supplier': i,
            }

            try:
                response = session.get('https://catalog.wb.ru/sellers/v2/catalog', params=params, headers=headers,
                                       timeout=60)

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')
                    if not os.path.exists('data'):
                        os.makedirs('data')
                    with open('data/exceptions_list.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{url}\n')
                    continue

                json_data = response.json()

            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            processed_count += 1
            print(f'Обработано URL: {processed_count}')  # Вывод количества обработанных URL

            try:
                data_products = json_data['data']['products']
                if not data_products:
                    continue
                result_list.append(url)
            except Exception as ex:
                print(f'json_data: {url} - {ex}')
                continue

            # Записываем данные в Excel каждые 1000 URL
            if len(result_list) >= batch_size:
                save_excel(result_list)
                result_list = []  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_excel(result_list)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results_wb'):
        os.makedirs('results_wb')

    if not os.path.exists(f'results/result_data.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_data.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_data.xlsx', sheet_name='Sellers')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_data.xlsx', mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name='Sellers',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    get_data_products_wb()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
