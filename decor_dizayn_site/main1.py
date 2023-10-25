import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import csv
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()




def get_data(data_list):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
    }

    count_urls = len(data_list)
    count = 1
    result_list = []

    with requests.Session() as session:
        for id, title, url in data_list:
            try:
                response = session.get(url=url, headers=headers, timeout=60)
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as ex:
                print(f"{url} - {ex}")
                continue
            try:
                title_site = soup.find('h2', class_='product_name').text.strip()
            except Exception:
                title_site = None
            try:
                price = soup.find('div', class_='price').text.strip()
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
            print(f'Обработано: {count}/{count_urls}')
            count += 1

    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    with open('data/decor_dizayn.csv', 'r', encoding='cp1251') as file:
        reader = csv.reader(file, delimiter=';')
        data_list = list(reader)
    data = get_data(data_list=data_list)
    save_excel(data)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
