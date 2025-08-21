import os
import time
from datetime import datetime
import json

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str | None:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


def get_products_urls(url: str, headers: dict) -> list[dict]:
    product_data_list = []

    with Session() as session:
        try:
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f'get_products_urls: {ex}')

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find_all('li', class_='menu-item-catalog')
        except Exception as ex:
            print(f'data: {ex}')

        for item in data:
            product_urls = []
            try:
                category_name = item.find('a', itemprop='url').text.strip()
            except Exception:
                category_name = None

            try:
                product_items = item.find('ul', class_='sub-menu').find_all('a')
            except Exception:
                continue

            for i, product_item in enumerate(product_items, 1):
                try:
                    product_url = product_item.get('href')
                except Exception:
                    continue

                product_urls.append(product_url)

                print(f'Получена ссылка: {i}')

            product_data_list.append(
                {
                    category_name: product_urls
                }
            )

            print(f'Обработана категория: {category_name}')

    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/product_data_list.json', 'a', encoding='utf-8') as file:
        json.dump(product_data_list, file, indent=4, ensure_ascii=False)

    return product_data_list


def get_products_data(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        product_data_list = json.load(file)

    result_data = []

    with Session() as session:
        for category_dict in product_data_list:
            for category_name, product_urls in category_dict.items():
                for product_url in product_urls:
                    try:
                        time.sleep(1)
                        html = get_html(url=product_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{product_url} - {ex}")
                        continue

                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'lxml')

                    try:
                        title = soup.find('h1').text.strip()
                    except Exception:
                        title = None

                    try:
                        content_data = soup.find('div', class_='entry-content')
                    except Exception as ex:
                        print(f'content_data: {product_url} - {ex}')
                        continue

                    try:
                        description = ''.join(i.text.strip().replace('\xa0', ' ') for i in content_data.find_all('p'))
                    except Exception:
                        description = ''

                    try:
                        characteristic = ''
                        characteristic_items = content_data.find('table').find_all('tr')
                        for characteristic_item in characteristic_items:
                            characteristic += '\n' + ' '.join(
                                c.text.strip().replace('\xa0', ' ') for c in characteristic_item.find_all('td'))
                    except Exception:
                        characteristic = ''

                    description = f'{description}\n{characteristic}'

                    try:
                        images_urls_list = []
                        images_items = content_data.find_all('figure', class_='gallery-item')
                        for image_item in images_items:
                            image_url = f"{image_item.find('a').get('href')}"
                            images_urls_list.append(image_url)
                        images_urls = ', '.join(images_urls_list)
                    except Exception:
                        images_urls = None

                    if not images_urls:
                        try:
                            images_urls = soup.find('div', class_='single-product-header').find('img').get('src')
                        except Exception:
                            images_urls = None

                    result_data.append(
                        {
                            'Название_позиции': title,
                            'Поисковые_запросы': f'{title}, {category_name}',
                            'Описание': description,
                            'Тип_товара': 'u',
                            'Цена': '',
                            'Валюта': '',
                            'Скидка': '',
                            'Единица_измерения': 1,
                            'Ссылка_изображения': images_urls,
                            'Наличие': '+',
                            'Идентификатор_товара': '',
                            'Идентификатор_группы': '',
                            'Личные_заметки': '',
                            'Ссылка_на_товар_на_сайте': '',
                        }
                    )

                    print(f'Обработано: {product_url}')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    directory = 'results'
    os.makedirs(directory, exist_ok=True)

    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='Export Products Sheet', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    # product_data_list = get_products_urls(url="https://neftemash-m.com/catalog/", headers=headers)
    result_data = get_products_data(file_path='data/product_data_list.json')
    save_excel(data=result_data, species='products')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
