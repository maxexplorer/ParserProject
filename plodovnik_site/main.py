import json
import time
from datetime import datetime
import os
import random


import requests
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter
import openpyxl


start_time = datetime.now()


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
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
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(ex)



# Получаем ссылки статей
def get_product_urls(headers: dict) -> list:
    """
    :param file_path: list
    :param headers: dict
    :return: None
    """

    product_urls_data = []
    plant_names_list = []
    pages = 309

    with requests.Session() as session:
        for page in range(1, pages + 1):

            try:
                time.sleep(1)
                url = f"https://plodovnik.ru/plants/?PAGEN_1={page}"
                html = get_html(url=url, headers=headers, session=session)
            except Exception as ex:
                print(f"{url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                production_items = soup.find('div', id='catalog-production-section').find_all('div', class_='plant-item')
            except Exception as ex:
                print(f'catalog_productions: {url} - {ex}')
                continue


            try:
                for item in production_items:
                    try:
                        plant_name = item.find('div', class_='plant-name').find('a').text.strip()
                    except Exception:
                        plant_name = None
                    try:
                        url_item = item.find('div', class_='plant-name').find('a').get('href')
                        product_url = f"https://plodovnik.ru{url_item}"
                    except Exception as ex:
                        print(f'product_url: {ex}')
                        continue

                    plant_names_list.append(plant_name)

                    product_urls_data.append(
                        {
                            plant_name: product_url
                        }
                    )
            except Exception as ex:
                print(ex)

            print(f'Обработано: {page}/{pages} страниц!')


        if not os.path.exists('data'):
            os.makedirs(f'data')

        with open(f'data/product_urls_data.json', 'w', encoding='utf-8') as file:
            json.dump(product_urls_data, file, indent=4, ensure_ascii=False)

        return plant_names_list


# Получаем данные о статьях
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_data = json.load(file)

    count = 1
    count_urls = len(product_urls_data)

    print(f'Всего {count_urls} ссылок!')

    result_data = []

    with requests.Session() as session:
        for dict_item in product_urls_data:
            for plant_name, product_url in dict_item.items():
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
                    data_items = soup.find('div', itemprop='description')
                except Exception as ex:
                    print(f'data_items: {ex}')
                    continue

                try:
                    description = data_items.find('div').find_next_sibling('div').text.strip()
                except Exception:
                    description = None


                result_data.append(
                    {
                        'Ссылка': product_url,
                        'Название': plant_name,
                        'Описание': description,
                    }
                )

                print(f'Обработано товаров: {count}/{count_urls}')

                count += 1

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, category_title: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/plodovnik.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/plodovnik.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=category_title, index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('results/plodovnik.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name=category_title, index=False)

    print(f'Данные сохранены в файл формата xlsx')


def main():
    # plant_names_list = get_product_urls(headers=headers)

    result_data = get_data('data/product_urls_data.json', headers=headers)

    save_excel(data=result_data, category_title='Description')


    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
