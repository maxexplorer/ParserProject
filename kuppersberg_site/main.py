import requests
import os
import json
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

start_time = datetime.now()


url = "https://kuppersberg.ru/categories/"


def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_category_urls(url, headers):
    category_urls_list = []

    with requests.Session() as session:
        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find('div', class_='catalog-main__wrap').find_all('div', class_='catalog-main__item')

            for item in data:
                category_url = f"https://kuppersberg.ru{item.find('a').get('href')}"

                category_urls_list.append(category_url)

        except Exception as ex:
            print(ex)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/category_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*category_urls_list, file=file, sep='\n')

def save_txt(data):

def main():
    category_urls_list = get_category_urls(url=url, headers=headers)


if __name__ == '__main__':
    main()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')