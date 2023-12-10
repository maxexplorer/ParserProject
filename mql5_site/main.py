import time

import requests
import os
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from random import randint
from datetime import datetime

start_time = datetime.now()

url = "https://www.mql5.com/ru/signals"
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


def auth_requests():
    pass


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

        if response.status_code != 200:
            print(f'{url}: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(ex)


# Получаем количество страниц
def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='paginatorEx').find_all('a', rel='nofollow')[-1].text)
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки товаров
def get_card_urls(headers: dict, start_value: int, finish_value: int) -> None:
    """

    :param headers: dict
    :param start_value: int
    :param finish_value: int
    :return: None
    """

    cur_date = datetime.now().strftime('%d-%m-%Y')
    total = finish_value - start_value
    count = 1

    with requests.Session() as session:
        card_urls_list = []

        # for id in range(start_value, finish_value + 1):
        for i in range(1, 2):
            try:
                url = f"https://www.mql5.com/ru/signals/{i}"
                # html = get_html(url=url, headers=headers, session=session)
                html = get_html(url=f"https://www.mql5.com/ru/signals/843451?source=Site+Signals+MT5+Tile",
                                headers=headers, session=session)
            except Exception as ex:
                print(ex)
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                free = soup.find('span', title='Бесплатно').text.strip()
            except Exception:
                free = ''

            try:
                price = soup.find('span', title='Бесплатно').text.strip()
            except Exception:
                price = ''




            try:
                title = soup.find('div', class_='s-plain-card__title').text.strip()
            except Exception as ex:
                print(f'Title: {i} - {ex}')
                title = ''

            try:
                author = soup.find('div', class_='s-plain-card__author').text.strip()
            except Exception as ex:
                print(f'Author: {i} - {ex}')
                title = ''

            if not os.path.exists('data'):
                os.makedirs('data')

            with open(f'data/data_{cur_date}.csv', 'a', encoding='cp1251', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        url,
                        title,
                        author,
                        price
                    )
                )

            count += 1

            print(f'Обработано: {count}/{total} страниц')

        # if not os.path.exists('data/cards'):
        #     os.makedirs(f'data/cards')
        #
        # with open(f'data/cards/card_urls_list_{meta_trader}.txt', 'w', encoding='utf-8') as file:
        #     print(*card_urls_list, file=file, sep='\n')


# Получаем данные о товарах
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        card_urls_list = [line.strip() for line in file.readlines()]

    count = len(card_urls_list)

    print(f'Всего {count} карточек')

    result_list = []

    # with requests.Session() as session:
    #     for i, product_url in enumerate(card_urls_list[:1], 1):
    #
    #         if i % 10 == 0:
    #             useragent = UserAgent()
    #
    #             headers = {
    #                 'Accept': '*/*',
    #                 'User-Agent': useragent.random
    #             }
    #
    #         try:
    #             html = get_html(url=product_url, headers=headers, session=session)
    #         except Exception as ex:
    #             print(f"{product_url} - {ex}")
    #             continue
    #
    #         with open('data/index.html', 'w', encoding='utf-8') as file:
    #             file.write(html)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'lxml')

    # print(f'Обработано карточек: {i}/{count}')


def save_csv(data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/results/{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('folder: Категория',
             'article: Артикул',
             'name: Название',
             'price: Цена',
             'image: Иллюстрация',
             'body: Описание',
             'amount : Количество',
             )
        )

    with open(f'data/results/{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    # meta_trader = 'mt5'

    start_value = 40000
    finish_value = 50000

    get_card_urls(headers=headers, start_value=start_value, finish_value=finish_value)

    # get_data(file_path='data/cards/card_urls_list.txt', headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
