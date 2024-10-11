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
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
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

                try:
                    revenue = item['revenue']
                except Exception:
                    revenue = None

                try:
                    revenue_by_year = item['revenue_by_year']
                    revenue2021 = revenue_by_year.get(2023)
                    revenue2022 = revenue_by_year.get(2022)
                    revenue2023 = revenue_by_year.get(2021)
                except Exception:
                    pass

                try:
                    key_indicators = item['key_indicators']
                    for key in key_indicators:
                        year = key['year']
                        code = key['code']
                        value = key['value']
                        if year in (2023, 2022, 2021) and code == 'profit':
                            if year == 2023:
                                profit2023 = value
                            elif year == 2022:
                                profit2022 = value
                            elif year == 2021:
                                profit2021 = value
                except Exception:
                    pass

                result_data.append(
                    {
                        'Название компании: RU': company_name_ru,
                        'Название компании: EN': company_name_en,
                        'ИНН': inn,
                        'Сайт': site,
                        'Общая выручка': revenue,
                        'Выручка за 2023': revenue2021,
                        'Выручка за 2022': revenue2022,
                        'Выручка за 2021': revenue2023,
                        'Чистая прибыль за 2021': profit2021,
                        'Чистая прибыль за 2022': profit2022,
                        'Чистая прибыль за 2023': profit2023,
                    }
                )

                print(f'Обработано: {i}')

                # Записываем данные в Excel каждые 100 URL
                if len(result_data) >= batch_size:
                    save_excel(data=result_data)
                    result_data.clear()  # Очищаем список для следующей партии

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
    file_path = f'{directory}/result_data.xlsx'

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
