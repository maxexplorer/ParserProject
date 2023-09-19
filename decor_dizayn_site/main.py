import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

exceptions_list = []

category_url_list = [
    "https://decor-dizayn.ru/catalog/belaya-lepnina/karnizy-belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/moldingi_belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/plintusy_belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/ugolki_belie/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/pilyastry/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/dekorativnye-elementi/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/paneli/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/skrytoe-osveshchenie/",
    "https://decor-dizayn.ru/catalog/rashodnye-materiali/kley/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/tsvetniye_plintusy/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dekorativnye-reyki/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/neo-klassika/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/afrodita/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/mramor/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/sultan/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/khay-tek/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dykhanie-2/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dykhanie-vostoka/"
]

# url = "https://decor-dizayn.ru/"
url = "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/tsvetniye_plintusy/?PAGEN_1=5"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

def get_html(url, headers):
    response = requests.get(url=url, headers=headers, timeout=60)
    html = response.text
    return html


def get_quantity_pages(urls_list):
    pass

def get_urls(category_url_list, headers):
    with requests.Session() as session:
        for url in category_url_list:
            try:
                html = get_html(url=url, headers=headers)

                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(f"{url} - {ex}")
                continue


def get_data(data_list):

    count = 1
    result_list = []

    with requests.Session() as session:
        for url in data_list:
            try:
                response = session.get(url=url, headers=headers, timeout=60)

                soup = BeautifulSoup(response.text, 'lxml')
            except Exception:
                exceptions_list.append(
                    url
                )
                continue
            try:
                title_site = soup.find(id='pagetitle').text.strip()
            except Exception:
                title_site = None
            try:
                price = soup.find(class_='price_value').text.strip()
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
    get_urls(category_url_list=category_url_list, headers=headers)

    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(html)

    # with open('data/decomaster.csv', 'r', encoding='cp1251') as file:
    #     reader = csv.reader(file, delimiter=';')
    #     data_list = list(reader)
    # print(f'Количество ссылок: {len(data_list)}')
    data = get_data(data_list=category_url_list)
    # save_excel(data)
    # if len(exceptions_list) > 0:
    #     with open('data/exceptions_list.csv', 'w', encoding='cp1251', newline='') as file:
    #         writer = csv.writer(file, delimiter=';')
    #         writer.writerows(exceptions_list)
    # execution_time = datetime.now() - start_time
    # print('Сбор данных завершен!')
    # print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
