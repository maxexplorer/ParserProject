import os
import re
import time
from datetime import datetime
from random import randint
from urllib.parse import urlparse, urlunparse

from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import openpyxl

import requests

start_time = datetime.now()

# Открываем файл Excel
workbook = openpyxl.load_workbook("data/data1.xlsm")


# Функция инициализации объекта chromedriver
def init_undetected_chromedriver():
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    return driver


def get_cleaned_url(product_url: str) -> str:
    # Парсим ссылку
    parsed_url = urlparse(product_url)

    # Собираем только основные части: схема, домен и путь
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    product_id = cleaned_url.rstrip('/').split('-')[-1]

    return product_id


# Функция получения ссылок товаров
def get_products_ids(driver: Chrome, pages: int, text: str) -> set[str]:
    products_ids = set()

    try:
        driver.get(url="https://www.ozon.ru/")
        time.sleep(3)

        try:
            input_text = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Искать на Ozon"]')
            input_text.clear()
            input_text.send_keys(text)
            time.sleep(3)
        except Exception as ex:
            print(f'input_text: {ex}')

        try:
            search_product = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Поиск"]')
            search_product.click()
            time.sleep(3)
        except Exception as ex:
            print(f'search_product: {ex}')

        for i in range(pages):
            # driver.execute_script("window.scrollTo(0, 4000);")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")

            time.sleep(randint(2, 3))

            driver.refresh()

            time.sleep(randint(2, 3))

            html = driver.page_source

            soup = BeautifulSoup(html, 'lxml')

            try:
                data_items = soup.find('div', class_='widget-search-result-container').find_all('div',
                                                                                                class_='tile-root')
            except Exception as ex:
                print(f'data_items: - {ex}')
                data_items = []

            for item in data_items:
                try:
                    product_url = f"https://www.ozon.ru{item.find('a').get('href')}"

                    product_id = get_cleaned_url(product_url=product_url)

                except Exception:
                    continue

                products_ids.add(product_id)

            print(len(products_ids))

        # if not os.path.exists('data'):
        #     os.makedirs('data')
        #
        # with open(f'data/products_ids_list_ozon.txt', 'a', encoding='utf-8') as file:
        #     print(*products_ids, file=file, sep='\n')

        return products_ids

    except Exception as ex:
        print(f'get_products_urls: {ex}')


def ozon_parser(driver: Chrome, workbook: openpyxl.Workbook, pages: int = 3):
    # Выбираем активный лист (или любой другой лист)
    ws = workbook['ОЗОН']

    # Словарь для хранения уже обработанных текстов и их product_ids
    processed_texts = {}

    try:
        for row in ws.iter_rows(min_row=4):
            text = row[1].value

            if not text:
                continue

            # Если text уже обработан, берем product_ids из словаря, иначе вызываем функцию
            if text in processed_texts:
                product_ids = processed_texts[text]
            else:
                product_ids = get_products_ids(driver=driver, pages=pages, text=text)
                processed_texts[text] = product_ids

            for cell in row:
                # Проверяем, что ячейка содержит строку
                if isinstance(cell.value, str) and 'https://' in cell.value:
                    try:
                        product_url = cell.value

                        driver.get(url=product_url)

                        time.sleep(randint(3, 5))

                        soup = BeautifulSoup(driver.page_source, 'lxml')
                    except Exception as ex:
                        continue

                    try:
                        out_of_stock = soup.find('h2', string=re.compile('Этот товар закончился'))
                        if out_of_stock:
                            # print(f'{url}: Этот товар закончился')
                            row[cell.column - 4].value = ''
                            row[cell.column - 3].value = 0
                            row[cell.column - 2].value = ''
                            continue
                    except Exception:
                        pass

                    try:
                        no_such_page = soup.find('h2', string=re.compile('Такой страницы не существует'))
                        if no_such_page:
                            row[cell.column - 4].value = ''
                            row[cell.column - 3].value = 'Такой страницы не существует'
                            row[cell.column - 2].value = ''
                            print(f'{product_url}: Такой страницы не существует')
                            continue
                    except Exception:
                        pass

                    try:
                        product_id = get_cleaned_url(product_url=product_url)
                    except Exception as ex:
                        product_id = ''

                    if product_id:
                        try:
                            product_position = product_ids.index(product_id) + 1
                        except Exception as ex:
                            # print(f'product_position: {product_url} - {ex}')
                            product_position = ''
                        row[cell.column + 2].value = product_position

                    try:
                        price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', string=re.compile(
                            'c Ozon Картой')).find_parent().text))
                    except Exception as ex:
                        # print(f'price - {ex}')
                        price = ''
                    row[cell.column - 4].value = price

                    try:
                        stor_item = soup.find('span', string=re.compile('Со склада')).text.strip()
                        storage = 'FBO' if 'Со склада Ozon' in stor_item else 'FBS'

                    except Exception as ex:
                        # print(f'storage - {ex}')
                        storage = ''
                    row[cell.column - 2].value = storage

                    try:
                        add_in_basket = driver.find_element(By.XPATH, '//div[contains(text(), "Добавить в корзину")]')
                        parent_element = add_in_basket.find_element(By.XPATH, "../..")
                        parent_element.click()
                        time.sleep(randint(3, 5))
                    except Exception as ex:
                        # print(f'add_in_basket: {ex}')
                        continue

                    try:
                        in_basket = driver.find_element(By.XPATH, '//span[contains(text(), "Корзина")]')
                        in_basket.click()
                        time.sleep(randint(3, 5))

                    except Exception as ex:
                        # print(f'in_basket: {ex}')
                        continue

                    try:
                        soup = BeautifulSoup(driver.page_source, 'lxml')
                        items = soup.find_all('input', inputmode='numeric')
                        quantity = items[0].get('max')
                    except Exception as ex:
                        # print(f'quantity - {ex}')
                        quantity = ''
                    row[cell.column - 3].value = quantity

                    try:
                        button_del1 = driver.find_element(By.XPATH, '//div[contains(text(), "Удалить выбранные")]')
                        button_del1.click()
                    except Exception as ex:
                        # print(f'button_del1: {ex}')
                        continue

                    try:
                        button_del2 = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '/html/body/div[4]/div/div[2]/div/div/section/div[3]/button'))
                        )
                        button_del2.click()

                        time.sleep(randint(3, 5))
                    except Exception as ex:
                        # print(f'button_del2: {ex}')
                        continue

                    print(f'{product_url}: price - {price}, quantity - {quantity}, storage - {storage}')

    except Exception as ex:
        print(ex)
    finally:
        workbook.save('data/result_data.xlsx')

def wildberries_parser(workbook):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wildberries.ru',
        'Referer': 'https://www.wildberries.ru/catalog/18172488/detail.aspx',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # Выбираем активный лист (или любой другой лист)
    ws = workbook['ВБ']

    for row in ws.iter_rows(min_row=4):
        for cell in row:
            # Проверяем, что ячейка содержит строку
            if isinstance(cell.value, str) and 'https://' in cell.value:
                url = cell.value
                prod_id = url.split('catalog')[-1].split('detail')[0].strip('/')

                params = {
                    'appType': '1',
                    'curr': 'rub',
                    'dest': '-1257786',
                    'spp': '30',
                    'nm': {prod_id},
                }

                try:
                    time.sleep(randint(1, 3))
                    response = requests.get('https://card.wb.ru/cards/v1/detail', params=params, headers=headers)
                    if response.status_code != 200:
                        print(f'{url}: {response.status_code}')
                except Exception as ex:
                    print(f'{url}: ex')
                    continue

                data = response.json()

                try:
                    quantity = data['data']['products'][0]['sizes'][0]['stocks'][0]['qty']
                    row[cell.column - 3].value = quantity
                except Exception:
                    print(f'{url}: Этот товар закончился')
                    row[cell.column - 4].value = ''
                    row[cell.column - 3].value = 0
                    row[cell.column - 2].value = ''
                    continue

                try:
                    storage_id = data['data']['products'][0]['sizes'][0]['stocks'][0]['dtype']
                    storage = 'FBO' if storage_id == 4 else 'FBS'
                except Exception:
                    storage = None
                row[cell.column - 2].value = storage

                try:
                    price = str(data['data']['products'][0]['salePriceU']).rstrip('00')
                except Exception:
                    price = None
                row[cell.column - 4].value = price

                print(f'{url}: price - {price}, quantity - {quantity}, storage - {storage}')

    workbook.save('data/result_data.xlsx')


def main():
    try:
        value = input('Введите значение:\n1 - Ozon\n2 - Wildberries\n3 - Оба сайта\n')

        pages = int(input('Введите количество страниц: \n'))

    except Exception:
        raise 'Введено неправильное значение:\n'

    driver = init_undetected_chromedriver()

    try:
        if value == '1':
            print('Сбор данных Ozon')
            ozon_parser(driver=driver, workbook=workbook, pages=pages)
            print('Сбор данных Ozon завершен')
        elif value == '2':
            print('Сбор данных Wildberries')
            wildberries_parser(workbook=workbook)
            print('Сбор данных Wildberries завершен')
        elif value == '3':
            print('Сбор данных Ozon')
            ozon_parser(workbook=workbook)
            print('Сбор данных Ozon завершен')

            print('Сбор данных Wildberries')
            wildberries_parser(workbook=workbook)
            print('Сбор данных Wildberries завершен')
        else:
            print('Введено неправильное значение')

    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
