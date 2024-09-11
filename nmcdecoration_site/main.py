import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

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
                response = session.get(url=url, headers=headers, timeout=60)

                if response.status_code != 200:
                    print(f'url: {url} status_code: {response.status_code}')
                    continue

                soup = BeautifulSoup(response.text, 'lxml')
            except Exception:
                exceptions_list.append(
                    [id, url]
                )
                continue

            try:
                title_site = soup.find('h1', {'data-hook': 'product-title'}).text.strip()
            except Exception:
                title_site = None
            try:
                price = soup.find('span', {'data-hook': 'formatted-primary-price'}).text.strip()
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

    with ExcelWriter('data/data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    with open('data/nmcdecoration.csv', 'r', encoding='cp1251') as file:
        reader = csv.reader(file, delimiter=';')
        data_list = list(reader)
    print(f'Количество ссылок: {len(data_list)}')
    data = get_data(data_list=data_list)
    save_excel(data)
    if len(exceptions_list) > 0:
        with open('data/exceptions_list.csv', 'w', encoding='cp1251', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(exceptions_list)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
