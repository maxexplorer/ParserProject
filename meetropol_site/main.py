import json
import os
import re
import time
from datetime import datetime
from random import randint

from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_urls_list

start_time = datetime.now()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

processed_urls = set()


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(
            soup.find('div', class_='catalog-pagination d-flex').find_all('li')[-1].find('a').get('href').split('=')[
                -1])
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_products_urls(category_urls_list: list, headers: dict) -> None:
    with Session() as session:
        for category_url in category_urls_list:
            products_urls = []

            print(f'Обрабатывается ссылка: {category_url}')

            try:
                time.sleep(randint(1, 3))
                html = get_html(url=category_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            # for page in range(1, pages + 1):
            for page in range(1, 2):
                category_page_url = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(randint(1, 3))
                    html = get_html(url=category_page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{category_page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('div',
                                              class_='catalog-items').find_all('div', class_='position-relative')
                    for product_item in product_items:
                        try:
                            product_url = f"https://meetropol.ru{product_item.find('a').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)

                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            get_products_data(products_urls=products_urls, headers=headers)


# Функция получения данных товаров
def get_products_data(products_urls: list, headers: dict) -> None:
    result_data = []

    count_urls = len(products_urls)

    print(f'Всего: {count_urls} товаров!')

    with Session() as session:
        for i, product_url in enumerate(products_urls, 1):
            try:
                time.sleep(randint(1, 3))
                html = get_html(url=product_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                element_list_items = soup.find_all('li', {'class': 'catalog-nav__item', 'itemprop': 'itemListElement'})
            except Exception as ex:
                print(f'element_list_items: {ex}')
                continue

            try:
                gender_item = element_list_items[2].text.strip()
            except Exception:
                gender_item = None

            if gender_item == 'Для неё':
                gender = 'Женщины'
            elif gender_item == 'Для него':
                gender = 'Мужчины'
            else:
                gender = None

            try:
                category_name = element_list_items[3].text.strip()
            except Exception:
                category_name = None

            try:
                subcategory_name = element_list_items[4].text.strip()
            except Exception:
                subcategory_name = None

            try:
                product_section = soup.find('section', class_='product-section')
            except Exception as ex:
                print(f'product_section: {ex}')
                continue

            try:
                name = product_section.find('h1').text.strip()
            except Exception:
                name = None

            try:
                price = int(''.join(
                    i for i in product_section.find('div', class_='catalog-product__cost').find('p').text.strip() if
                    i.isdigit()))
            except Exception:
                price = None

            try:
                description = product_section.find('div',
                                                   class_='d-flex flex-column gap-4 gap-sm-0 flex-sm-row justify-content-between'
                                                   ).find_next_sibling('p').text.strip()
            except Exception:
                description = None

            try:
                color = ', '.join(k for k in (c.get('title') for c in product_section.find(
                    'div', class_='filter-color__wrapper').find_all('label')) if k.isalpha())
            except Exception:
                color = ' '

            result_data.append(
                {
                    'UUID': None,
                    'Тип': category_name,
                    'Группы': subcategory_name,
                    'Пол': gender,
                    'Код': None,
                    'Наименование': name,
                    'Внешний код': product_url,
                    'Артикул': None,
                    'Единица измерения': None,
                    'Вес': None,
                    'Объем': None,
                    'Весовой товар': None,
                    'Разливной товар': None,
                    'Цена товара': price,
                    'Валюта (Цена продажи)': 'руб',
                    'Закупочная цена': None,
                    'Валюта (Закупочная цена)': 'руб',
                    'Неснижаемый остаток': None,
                    'Штрихкод EAN13': None,
                    'Штрихкод EAN8': None,
                    'Штрихкод Code128': None,
                    'Штрихкод UPC': None,
                    'Описание': description,
                    'Признак предмета расчета': 'Товар',
                    'Запретить скидки при продаже в розницу': None,
                    'Минимальная цена': None,
                    'Валюта (Минимальная цена)': 'руб',
                    'Страна': 'Россия',
                    'НДС': None,
                    'Система налогообложения': None,
                    'Поставщик': None,
                    'Остаток': None,
                    'Изображение(файл)': None,
                    'Изображение(ссылка)': None,
                    'ГТД': None,
                    'Код товара модификации': None,
                    'Характеристика:эко': None,
                    'Характеристика:Цвет': color,
                    'Упаковка:мешок': None,
                    'Упаковка(ШК):мешок:EAN8': None,
                    'Алкогольная продукция': None,
                    'Содержит акцизную марку': None,
                }
            )

            print(f'Обработано: {i}/{count_urls} товаров!')

        save_excel(data=result_data)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_products_meetropol.xlsx'

    # Если файл не существует, создаем его с пустым DataFrame
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='Data')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='Data',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    get_products_urls(category_urls_list=category_urls_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
