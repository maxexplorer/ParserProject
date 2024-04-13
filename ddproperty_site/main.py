import time
import os
import random
import re
from datetime import datetime

import requests
from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter
import openpyxl


start_time = datetime.now()


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/123.0.0.0 Safari/537.36'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
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
            soup.find('div', class_='listing-pagination').find_all('li')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages



# Получаем ссылки товаров
def get_property_urls(headers: dict) -> None:
    """
    :param headers: dict
    :return: None
    """

    district_url = "https://www.ddproperty.com/en/property-for-sale/1?district_code%5B0%5D=TH8404&freetext=Ko+Samui&search=true"

    with Session() as session:
            try:
                html = get_html(url=district_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{district_url} - {ex}")
                raise requests.RequestException('Ссылка недоступна')

            pages = get_pages(html=html)
            print(f'Всего: {pages} страниц!')

            for page in range(1, pages + 1):
                page_district_url = f"https://www.ddproperty.com/en/property-for-sale/{page}?district_code%5B0%5D=TH8404&freetext=Ko+Samui&search=true"
                try:
                    html = get_html(url=page_district_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_district_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    property_data = soup.find_all('div', class_='listing-card listing-id')

                    for item in property_data:
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


# Функция для записи данных в формат xlsx
def save_excel(data: list, category_title: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/Чуйские известия.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/Чуйские известия.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=category_title, index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('results/Чуйские известия.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name=category_title, index=False)

    print(f'Данные сохранены в файл формата xlsx')


def main():


    get_property_urls(headers=headers)



    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
