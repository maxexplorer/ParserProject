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

# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: requests.sessions.Session) -> str:
    """
    :param url: str
    :param headers: dict
    :param session: requests.sessions.Session
    :return: str
    """

    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


# Получаем ссылки всех категорий товаров
def get_category_urls(url:str, headers:dict) ->list:
    """
    :param url: str
    :param headers: dict
    :return: list
    """

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

    return category_urls_list

# Получаем ссылки всех подкатегорий товаров
def get_subcategory_urls(file_path:str, headers:dict) ->(str, list):
    """
    :param file_path: str
    :param headers: dict
    :return: str, list
    """


    with open(file_path, 'r', encoding='utf-8') as file:
        category_urls_list = [line.strip() for line in file.readlines()]

    subcategory_urls_list = []

    with requests.Session() as session:

        for category_url in category_urls_list[0:1]:
            html = get_html(url=category_url, headers=headers, session=session)

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find('div', class_='category__top-block__items').find_all('a', class_='category__top-block__item')

                for item in data:
                    subcategory_url = f"https://kuppersberg.ru{item.get('href')}"
                    name = subcategory_url.split('/')[-3].strip()
                    subcategory_urls_list.append(subcategory_url)

            except Exception as ex:
                print(ex)

    return name, subcategory_urls_list

def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='module-pagination').find_all('a')[-2].text)
    except Exception:
        pages = 1
    return pages


def save_txt(name, data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/{name}.txt', 'w', encoding='utf-8') as file:
        print(*data, file=file, sep='\n')


def main():
    # category_urls_list = get_category_urls(url=url, headers=headers)
    # save_txt(name='category_urls_list', data=category_urls_list)

    name, subcategory_urls_list = get_subcategory_urls(file_path='data/category_urls_list.txt', headers=headers)
    save_txt(name=name, data=subcategory_urls_list)


if __name__ == '__main__':
    main()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')
