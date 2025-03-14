import json
import os
import time
from datetime import datetime

from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

start_time = datetime.now()

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://navigator.sk.ru',
    'priority': 'u=1, i',
    'referer': 'https://navigator.sk.ru/?q=N4IgZiBcoC4IYHMDOB9GBPADgUyiA9gE4gA0IAloQDZShiH4C2epIM%2BLAvmY9beA2aQQrdlzIw%2B0AUxYSOwkNxBIArgCNG5GAGF8qgHYwoARjIBjJpjgH0KQtgBu2A6tzT6sxfPEhzUukE5NgURTmUkPABaRmxGdWxCFCRyA3NcMkxTTiA',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'cookie': 'navigator_session_logs=92ef0c5ffd7ac9b106be177f7dea5e58; navigator_session=eyJfZnJlc2giOmZhbHNlLCJ1c2VyX2lkIjowfQ.Z73AIw.QxW5p2A-Mf_ytB31ZmVIvNq62Pc; spid=1740482256992_4b68d3c9dc7e1a2556ce419c4726c7ca_w4urgjo2cvqbmofd; _ym_uid=1728550747944351283; _ym_d=1740482260; _ym_isad=2; spsc=1740488734687_37e21651eeaaf4829ff0077beff9ab2b_e6cfb3ea8f0a0fa28cc6ebefdcae8ea5; _ym_visorc=w',
}

# Функция получения данных товаров
def get_data(headers: dict) -> None:
    result_data = []
    batch_size = 100

    with Session() as session:
        for i in range(1, 50):
            json_data = {
                'sort': '-member_since',
                'page': i,
                'filters': {
                    'tags_type': 'or',
                },
                'limit': 100,
            }

            try:
                time.sleep(1)
                response = session.post(
                    'https://navigator.sk.ru/navigator/api/search/only_companies/',
                    headers=headers,
                    json=json_data,
                )

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')
                    continue

                json_data = response.json()

            except Exception as ex:
                print(f'response: {ex}')
                continue

            try:
                data = json_data['companies']
            except Exception:
                raise 'not data'

            if not data:
                break

            for item in data:
                try:
                    company_name_ru = item['name']['ru']
                except Exception:
                    company_name_ru = None

                try:
                    company_name_en = item['name']['en']
                except Exception:
                    company_name_en = None

                try:
                    inn = item['inn']
                except Exception:
                    inn = None

                try:
                    site = item['site']
                except Exception:
                    site = None

                revenue2021 = None
                revenue2022 = None
                revenue2023 = None

                try:
                    revenue_by_year = item['revenue_by_year']
                    revenue2021 = revenue_by_year.get('2021')
                    revenue2022 = revenue_by_year.get('2022')
                    revenue2023 = revenue_by_year.get('2023')
                except Exception:
                    pass

                profit2021 = None
                profit2022 = None
                profit2023 = None

                try:
                    key_indicators = item['key_indicators']
                    for key in key_indicators:
                        year = key['year']
                        code = key['code']
                        value = key['value']
                        if year in (2021, 2022, 2023) and code == 'profit':
                            if year == 2021:
                                profit2021 = value
                            elif year == 2022:
                                profit2022 = value
                            elif year == 2023:
                                profit2023 = value
                except Exception:
                    pass


                try:
                    average_number_of_employees = item['average_number_of_employees']
                except Exception:
                    average_number_of_employees = None

                result_data.append(
                    {
                        'Название компании: RU': company_name_ru,
                        'Название компании: EN': company_name_en,
                        'ИНН': inn,
                        'Сайт': site,
                        'Выручка за 2023': revenue2023,
                        'Выручка за 2022': revenue2022,
                        'Выручка за 2021': revenue2021,
                        'Чистая прибыль за 2023 (убыток)': profit2023,
                        'Чистая прибыль за 2022 (убыток)': profit2022,
                        'Чистая прибыль за 2021 (убыток)': profit2021,
                        'Количество сотрудников': average_number_of_employees
                    }
                )


                # Записываем данные в Excel каждые 100 URL
                if len(result_data) >= batch_size:
                    save_excel(data=result_data)
                    result_data.clear()  # Очищаем список для следующей партии

            print(f'Обработано: {i}')

        # Записываем оставшиеся данные в Excel
        if result_data:
            save_excel(data=result_data)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data1.xlsx'

    # Если файл не существует, создаем его с пустым DataFrame
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Компании', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='Компании')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name='Компании',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    get_data(headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
