import re
import time
from random import randint

import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import json
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

category_urls_list = [
    "https://hiwooddecor.ru/catalog/paneli-iz-fitopolimera/",
    "https://hiwooddecor.ru/catalog/finishnye-moldingi-dlya-paneley/",
    "https://hiwooddecor.ru/catalog/karnizy-iz-fitopolimera/",
    "https://hiwooddecor.ru/catalog/moldingi-i-ugly/",
    "https://hiwooddecor.ru/catalog/plintusy/",
    "https://hiwooddecor.ru/catalog/profili-podsvetku/",
    "https://hiwooddecor.ru/catalog/dekorirovannye-reyki/",
    "https://hiwooddecor.ru/catalog/klei/",
    "https://hiwooddecor.ru/catalog/reklamnaya-produktsiya/"
]

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


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
            print(response.status_code)

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
        pages = int(soup.find('div', class_='pagination__catalog').find_all('li')[-1].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки товаров
def get_product_urls(category_urls_list: list, headers: dict) -> None:
    """
    :param file_path: list
    :param headers: dict
    :return: None
    """

    count_urls = len(category_urls_list)

    print(f'Всего: {count_urls} категорий')

    product_urls_list = []

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                product_url = f"{category_url}?&PAGES_1={page}"
                try:
                    time.sleep(randint(1, 3))
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find('div', class_='catalog__list').find_all('div', class_='catalog__list-item')
                    for item in data:
                        try:
                            url = f"https://hiwooddecor.ru{item.find('a', class_='title').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(url)
                except Exception as ex:
                    print(ex)

            print(f'Обработано: {i}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*product_urls_list, file=file, sep='\n')


# Получаем данные о товарах
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(product_urls_list)

    result_list = []
    image_urls_list = []

    with requests.Session() as session:
        for j, product_url in enumerate(product_urls_list, 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                category = soup.find('div', class_='breadcrumbs').find_all('a')[1].text.strip()
            except Exception:
                category = ''

            try:
                images_data = soup.find('div', class_='section__preview-images').find_all(
                    'a', class_='section__preview-img_item')
            except Exception as ex:
                print(f'{product_url} - {ex}')
                images_data = ''

            try:
                info_data = soup.find('div', class_='section__preview-info')
            except Exception as ex:
                print(f'{product_url} - {ex}')
                info_data = ''

            try:
                title = info_data.find('h1').text.strip()
            except Exception:
                title = None

            try:
                price = info_data.find('div', class_='price').text.strip()
            except Exception:
                price = ''

            try:
                dimensions = info_data.find('span', class_='attr').text.strip()
            except Exception:
                dimensions = ''

            try:
                description = info_data.find('p').text.strip()
            except Exception:
                description = None

            try:
                for item_url in images_data:
                    img_url = f"https://hiwooddecor.ru{item_url.get('href')}"
                    image_urls_list.append(img_url)
            except Exception as ex:
                print(f'image_data: {product_url} - {ex}')

            try:
                diagram_url = f"https://hiwooddecor.ru{info_data.find('img', class_='diagram').get('src')}"
                if diagram_url:
                    image_urls_list.append(diagram_url)
            except Exception:
                diagram_url = ''

            try:
                image_title = ', '.join(item_url.get('href').split('/')[-1] for item_url in images_data)
                if diagram_url:
                    image_title += f", {diagram_url.split('/')[-1]}"
            except Exception:
                image_title = ''

            result_list.append(
                {'Название товара': title,
                 'Категория товара': category,
                 'Ссылка': product_url,
                 'Изображения': image_title,
                 'Размеры': dimensions,
                 'Описание': description,
                 'Цена': price,
                 }
            )

            print(f'Обработано: {j}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/image_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*image_urls_list, file=file, sep='\n')

    return result_list


def download_imgs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, img_url in enumerate(image_urls_list, 1):
        image_title = img_url.split('/')[-1]

        response = requests.get(url=img_url)

        if not os.path.exists('images'):
            os.mkdir('images')

        with open(f"images/{image_title}", "wb") as file:
            file.write(response.content)

        print(f'Обработано: {k}/{count_urls} изображений')

def save_excel(data):
    if not os.path.exists('data'):
        os.makedirs('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    # get_product_urls(category_urls_list=category_urls_list, headers=headers)
    result_list = get_data(file_path="data/product_urls_list.txt", headers=headers)
    save_excel(data=result_list)
    download_imgs(file_path="data/image_urls_list.txt")
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
