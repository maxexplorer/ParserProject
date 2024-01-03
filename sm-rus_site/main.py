import random
import re
import time

import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()

url = "https://sm-rus.ru/"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://sm-rus.ru/smeg/duhovye-shkafy/",
    "https://sm-rus.ru/smeg/varochnye-paneli/",
    "https://sm-rus.ru/smeg/vytjazhki/",
    "https://sm-rus.ru/smeg/sushilnye-mashiny/",
    "https://sm-rus.ru/smeg/holodilniki/",
    "https://sm-rus.ru/smeg/varochnye-centry/",
    "https://sm-rus.ru/smeg/mikrovolnovye-pechi/",
    "https://sm-rus.ru/smeg/kofemashiny/",
    "https://sm-rus.ru/smeg/podogrevateli/",
    "https://sm-rus.ru/smeg/vakuumnyie/",
    "https://sm-rus.ru/smeg/yashchiki-somele/",
    "https://sm-rus.ru/smeg/posudomoechnye-mashiny/",
    "https://sm-rus.ru/smeg/stiralnye-mashiny/",
    "https://sm-rus.ru/smeg/aksessuary/",
    "https://sm-rus.ru/smeg/chainiki/",
    "https://sm-rus.ru/smeg/kofemolki/",
    "https://sm-rus.ru/smeg/tostery/",
    "https://sm-rus.ru/smeg/blendery/",
    "https://sm-rus.ru/smeg/kofevarki/",
    "https://sm-rus.ru/smeg/vspenivateli-moloka/",
    "https://sm-rus.ru/smeg/sokovyzhimalki/",
    "https://sm-rus.ru/smeg/miksery/",
    "https://sm-rus.ru/smeg/smesiteli/",
    "https://sm-rus.ru/smeg/moyki/",
    "https://sm-rus.ru/smeg/pechi/",
    "https://sm-rus.ru/smeg/stakanomoechnye-mashiny/",
    "https://sm-rus.ru/smeg/kholodilnoe-oborudovanie/",
    "https://sm-rus.ru/smeg/posudomoechnye-mashiny-pro/",
    "https://sm-rus.ru/smeg/kotlomoechnye-mashiny-pro/",
    "https://sm-rus.ru/smeg/aksessuary_pro/"
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
        pages = int(
            soup.find('ul', class_='pages-nav__list').find_all('li', class_='pages-nav__item')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки всех категорий товаров
def get_category_urls(url: str, headers: dict) -> None:
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
            data = soup.find('ul', class_='dropdown-menu js-dropdown').find_all('li')

            for item in data:
                category_url = f"https://sm-rus.ru{item.find('a').get('href')}"

                category_urls_list.append(category_url)

        except Exception as ex:
            print(ex)

        if not os.path.exists('data/categories'):
            os.makedirs('data/categories')

        with open(f'data/categories/category_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*category_urls_list, file=file, sep='\n')


# Получаем ссылки товаров
def get_product_urls(category_urls_list: list, headers: dict) -> None:
    """
    :param file_path: list
    :param headers: dict
    :return: None
    """

    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            product_urls_list = []

            name_category = category_url.split('/')[-2]

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В категории {name_category}: {pages} страниц')

            for page in range(1, pages + 1):
                page_product_url = f"{category_url}/?PAGEN_7={page}"
                try:
                    html = get_html(url=page_product_url, headers=headers, session=session)

                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('div', class_='catalog-card__text-content')

                    for item in data:
                        try:
                            product_url = f"https://sm-rus.ru{item.find('a', class_='card-type-and-title catalog-card__type-and-title').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            print(f'Обработано: {i}/{count_urls} категорий')

            if not os.path.exists('data/products'):
                os.makedirs(f'data/products')

            with open(f'data/products/{name_category}.txt', 'w', encoding='utf-8') as file:
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

    count = len(product_urls_list)

    print(f'Всего {count} товаров')

    result_list = []

    with requests.Session() as session:
        for i, product_url in enumerate(product_urls_list, 1):
            try:
                time.sleep(random.randint(1, 3))
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                folder_item = soup.find('ul', class_='breadcrumbs').find_all('li', class_='breadcrumbs__item')[
                    1].text.strip()
            except Exception:
                folder_item = ''

            # try:
            #     characteristic_item = \
            #         soup.find('span', string=re.compile('ОБЩИЕ ХАРАКТЕРИСТИКИ')).find_next().find_next().find_all('div',
            #                                                                                                       class_='characteristics__row')[
            #             0].find('span', class_='characteristics__property').text.strip()
            # except Exception:
            #     characteristic_item = ''

            try:
                characteristic_item1 = soup.find('span', string=re.compile(
                    'ОБЩИЕ ХАРАКТЕРИСТИКИ')).find_next().find_next().find(
                    'span', string=re.compile('Способ установки')).find_next().find_next().text.strip()
            except Exception:
                characteristic_item1 = ''

            try:
                characteristic_item2 = soup.find('span', string=re.compile(
                    'ОБЩИЕ ХАРАКТЕРИСТИКИ')).find_next().find_next().find(
                    'span', string=re.compile('Форм-фактор')).find_next().find_next().text.strip()
                if 'классический' in characteristic_item2:
                    characteristic_item2 = 'Классический'

            except Exception:
                characteristic_item2 = ''

            try:
                characteristic_item3 = soup.find('span', string=re.compile(
                    'ОБЩИЕ ХАРАКТЕРИСТИКИ')).find_next().find_next().find('span', string=re.compile(
                    'Вид холодильника')).find_next().find_next().text.strip()
                if 'Винный шкаф' in characteristic_item3:
                    characteristic_item3 = 'Винный шкаф'

            except Exception:
                characteristic_item3 = ''

            folder = f'{folder_item}/{characteristic_item1}/{characteristic_item2}/{characteristic_item3}'

            try:

                name = soup.find('h1', class_='page-title').text.strip()
            except Exception:
                name = ''

            try:
                article = soup.find('div',
                                    class_='card-info__product-code js-card-info-product-code').find_next().find_next().text.strip()
            except Exception:
                article = ''

            try:
                price = ''.join(k for k in soup.find('span', class_='big-price__price').text.strip() if k.isdigit())
            except Exception:
                price = ''

            try:
                image_data = soup.find_all('a', class_='product-page-card__slider-link')
                image = ''
                for item in image_data:
                    url = 'https://sm-rus.ru' + item.get('href')
                    image += f'{url}, '
            except Exception:
                image = ''

            try:
                description = ' '.join(
                    soup.find('div', class_='product-description _vr-m-s js-product-description').text.strip().split())
            except Exception:
                description = ''

            try:
                characteristics = ' '.join(item for item in
                                           soup.find('section', class_='characteristics _vr-m-s').find('div',
                                                                                                       class_='characteristics__wrap').text.split())
            except Exception:
                characteristics = ''

            body = f"{description} {characteristics}"

            vendor = 'Smeg'

            amount = 1

            result_list.append(
                (
                    vendor,
                    f"Smeg/{folder}",
                    article,
                    name,
                    price,
                    image,
                    body,
                    amount,
                )
            )

            print(f'Обработано товаров: {i}/{count}')

    return result_list


def save_csv(name, data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/results/{name}_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('vendor: Производитель',
             'folder: Категория',
             'article: Артикул',
             'name: Название',
             'price: Цена',
             'image: Иллюстрация',
             'body: Описание',
             'amount : Количество'
             )
        )

    with open(f'data/results/{name}_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    get_category_urls(url=url, headers=headers)

    get_product_urls(category_urls_list=category_urls_list, headers=headers)

    directory = 'data\products'
    for filename in os.listdir(directory)[5:6]:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            name = file_path.split('\\')[-1].split('.')[0]
            print(f'Обрабатывается категория {name}')
            result_list = get_data(file_path=file_path, headers=headers)
            save_csv(name=name, data=result_list)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
