import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

exceptions_list = []


def get_data(data_list):
    useragent = UserAgent()

    headers = {
        'accept': '*/*',
        'user-agent': useragent.random
    }

    count = 1
    result_list = []

    with requests.Session() as session:
        for id, _, url in data_list:
            try:
                response = session.get(url=url, headers=headers, timeout=60)

                soup = BeautifulSoup(response.text, 'lxml')
            except Exception:
                exceptions_list.append(
                    [id, url]
                )
                continue
            try:
                title = soup.find(class_='prod-info-main').text.strip()
            except Exception:
                title = None
            try:
                price = soup.find(class_='prod-price').text.strip('RUB')
            except Exception:
                price = None

            result_list.append(
                (
                    id,
                    title,
                    url,
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
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
