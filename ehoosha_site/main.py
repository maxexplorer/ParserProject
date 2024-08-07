import time
from datetime import datetime
import os
import random

import requests
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter

start_time = datetime.now()


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://ehoosha.com/?module=news&action=list",
    "https://ehoosha.com/?module=articles&action=list&rubrics=37",
    "https://ehoosha.com/?module=articles&action=list&rubrics=11",
    "https://ehoosha.com/?module=articles&action=list&rubrics=1"
]


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
            print(f'status_code: {response.status_code}')

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
        pages = int(
            soup.find('div', class_='paginator').find_all('a', class_='item-page')[-1].text.strip())
    except Exception as ex:
        print(f'get_pages: {ex}')
        pages = 1

    return pages


# Получаем ссылки статей
def get_article_urls(category_urls_list: list, headers: dict) -> None:
    """
    :param file_path: list
    :param headers: dict
    :return: None
    """

    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            article_urls_list = []

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            pages = get_pages(html=html)
            print(f'В категории {category_url}: {pages} страниц!')

            for page in range(1, pages + 1):
                page_product_url = f"{category_url}&page={page}"
                try:
                    time.sleep(random.randint(1, 3))
                    html = get_html(url=page_product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    category_title = soup.find('div', class_='spisok_rubrics').find('div', class_='head').text.strip()
                except Exception:
                    category_title = 'Общая'

                try:
                    data = soup.find('div', class_='articles-block').find_all('div', class_='item')

                    for item in data:
                        try:
                            product_url = f"https://ehoosha.com{item.find('div', class_='title').find('a').get('href')}"
                        except Exception as ex:
                            print(f'product_url: {ex}')
                            continue
                        article_urls_list.append(product_url)
                except Exception as ex:
                    print(f'data: {ex}')

                print(f'Обработано: {page}/{pages} страниц!')

            print(f'Обработано: {i}/{count_urls} категорий!')

            if not os.path.exists('data'):
                os.makedirs(f'data')

            with open(f'data/{category_title}.txt', 'w', encoding='utf-8') as file:
                print(*article_urls_list, file=file, sep='\n')


# Получаем данные о статьях
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        article_urls_list = [line.strip() for line in file.readlines()]

    count = len(article_urls_list)

    print(f'Всего {count} статей!')

    result_data = []

    with requests.Session() as session:
        for i, article_url in enumerate(article_urls_list, 1):
            try:
                time.sleep(random.randint(1, 3))
                html = get_html(url=article_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{article_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find('div', class_='content-details')
            except Exception as ex:
                print(f'data: {ex}')
                continue
            try:
                article_title = data.find('h1', class_='head').text.strip()
            except Exception:
                article_title = ''

            try:
                date = data.find('div', class_='date').text.strip()
            except Exception:
                date = ''

            try:
                statistic = data.find('div', class_='stats').text.strip()
            except Exception:
                statistic = ''
            try:
                text = ' '.join(data.find('div', class_='item-content').text.split())
            except Exception:
                text = ''

            result_data.append(
                {
                    'Ссылка': article_url,
                    'Название статьи': article_title,
                    'Дата издания': date,
                    'Количество просмотров': statistic,
                    'Текст': text,
                }
            )

            print(f'Обработано товаров: {i}/{count}')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, category_title: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/Эхо Оша.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/Эхо Оша.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=category_title, index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('results/Эхо Оша.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name=category_title, index=False)

    print(f'Данные сохранены в файл формата xlsx')


def main():

    # get_article_urls(category_urls_list=category_urls_list, headers=headers)

    directory = 'data'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            category_title = file_path.split('\\')[-1].split('.')[0]
            print(f'Обрабатывается категория {category_title}')
            result_list = get_data(file_path=file_path, headers=headers)
            save_excel(data=result_list, category_title=category_title)


    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
