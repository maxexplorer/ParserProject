import time

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

exceptions_list = []


def get_data(data_list):
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
    }

    count = 1
    result_list = []

    with requests.Session() as session:
        for id, title, url in data_list:
            try:
                time.sleep(1)
                response = session.get(url=url, headers=headers, timeout=60)

                soup = BeautifulSoup(response.text, 'lxml')
            except Exception:
                exceptions_list.append(
                    [id, title, url]
                )
                continue
            try:
                title_site = soup.find('h1', itemprop='name').text.strip()
            except Exception:
                title_site = None
            try:
                price = soup.find('h2', class_='prod-info-price').text.strip('RUB')
            except Exception:
                price = None

            result_list.append(
                (
                    id,
                    title,
                    url,
                    title_site,
                    price
                )
            )
            print(count)
            count += 1
    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    try:
        with open('data/evroplast.csv', 'r', encoding='cp1251') as file:
            reader = csv.reader(file, delimiter=';')

            data_list = list(reader)

        print(f'Количество ссылок: {len(data_list)}')
        data = get_data(data_list=data_list)
        save_excel(data)
        if len(exceptions_list) > 0:
            with open('data/exceptions_list.csv', 'w', encoding='cp1251', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerows(exceptions_list)
    except Exception as ex:
        print(f"Произошла ошибка: {ex}")
        input("Нажмите Enter, чтобы выйти...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
