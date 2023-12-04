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


def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(
            soup.find('div', class_='module-category__nav__pagin pagination').find_all('a', class_='pagination__one')[
                -2].text)
    except Exception:
        pages = 1
    return pages


# Получаем ссылки всех категорий товаров
def get_category_urls(url: str, headers: dict) -> list:
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

        if not os.path.exists('data/category'):
            os.makedirs('data/category')

        with open(f'data/category/category_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*data, file=file, sep='\n')


# Получаем ссылки всех подкатегорий товаров
def get_subcategory_urls(file_path: str, headers: dict) -> None:
    """
    :param file_path: str
    :param headers: dict
    :return: None
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        category_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    with requests.Session() as session:

        for i, category_url in enumerate(category_urls_list, 1):
            subcategory_urls_list = []

            html = get_html(url=category_url, headers=headers, session=session)

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find_all('a', class_='k-filters__one__value')

            except Exception as ex:
                print(ex)

            if data:
                for item in data:
                    subcategory_url = f"https://kuppersberg.ru{item.get('href')}"
                    if subcategory_url is None:
                        continue
                    name = subcategory_url.split('/')[-3].strip()
                    subcategory_urls_list.append(subcategory_url)
            else:
                subcategory_urls_list.append(category_url)
                name = category_url.split('/')[-2]

            if not os.path.exists('data'):
                os.makedirs('data/subcategory')

            with open(f'data/subcategory/{name}.txt', 'w', encoding='utf-8') as file:
                print(*subcategory_urls_list, file=file, sep='\n')

            print(f'Обработано: {i}/{count_urls} категорий')


# Получаем ссылки товаров
def get_product_urls(file_path: str, headers: dict) -> None:
    """
    :param file_path: str
    :param headers: dict
    :return: None
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        subcategory_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(subcategory_urls_list)
    print(f'Всего: {count_urls} подкатегорий')

    with requests.Session() as session:
        for i, subcategory_url in enumerate(subcategory_urls_list, 1):
            try:
                html = get_html(url=subcategory_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{subcategory_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В {i} категории: {pages} страниц')

        #     for page in range(1, pages + 1):
        #         product_url = f"{category_url}?PAGEN_1={page}"
        #         try:
        #             time.sleep(1)
        #             html = get_html(url=product_url, headers=headers, session=session)
        #         except Exception as ex:
        #             print(f"{url} - {ex}")
        #             continue
        #         soup = BeautifulSoup(html, 'lxml')
        #
        #         try:
        #             data = soup.find_all('a', class_='thumb shine')
        #             for item in data:
        #                 try:
        #                     url = "http://teledom46.ru" + item.get('href')
        #                 except Exception as ex:
        #                     print(ex)
        #                     continue
        #                 product_urls_list.append(url)
        #         except Exception as ex:
        #             print(ex)
        #
        #         print(f'Обработано: {page}/{pages} страниц')
        #
        #     print(f'Обработано: {i}/{count_urls} категорий')
        #
        # if not os.path.exists('data'):
        #     os.mkdir('data')
        #
        # with open('data/product_url_list.txt', 'w', encoding='utf-8') as file:
        #     print(*product_urls_list, file=file, sep='\n')


def main():
    # get_category_urls(url=url, headers=headers)
    # get_subcategory_urls(file_path='data/category/category_urls_list.txt', headers=headers)
    directory = 'data\subcategory'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            get_product_urls(file_path=file_path, headers=headers)


if __name__ == '__main__':
    main()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')
