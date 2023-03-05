import requests
from bs4 import BeautifulSoup
import os
import json
import csv
from pandas import DataFrame, ExcelWriter
import openpyxl

url = "https://kladr-rf.ru/"
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36'
}


def get_html(url, headers):
    response = requests.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

    html = response.text
    return html


def get_data(html):
    city_streets = []

    soup = BeautifulSoup(html, 'lxml')

    items = soup.find(class_='pb-2 fs-5 fw-bold border-bottom', text='Города').find_next().find_all('li')
    for item in items:
        try:
            url = "https://kladr-rf.ru" + item.find('a').get('href')
            city = item.text.strip().split()[0]
            print(url, city)
            for i in
        except Exception:
            continue



    return city_streets


def main():
    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    get_data(html)
    # result_list = []
    # for i in range(1, 2):
    #     url = f"https://kladr-rf.ru/{str(i).zfill(2)}/"
    #     html = get_html(url=url, headers=headers)
    # result_list.extend(get_data(html))


if __name__ == '__main__':
    main()
