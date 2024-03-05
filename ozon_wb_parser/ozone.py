import json
import os
import re
import time
from datetime import datetime
from random import randint

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

# Функция получения количества страниц
def get_pages(html: str = None) -> int:
    try:
        soup = BeautifulSoup(html, 'lxml')

        pages = int(soup.find('div', class_='eo6').find_all('a')[-2].text)

        print(f'Всего страниц: {pages}')
    except Exception:
        pages = 1

    return pages


# Функция получения ссылокб рейтинга, количества отзывов всех продуктов продавца
def get_urls_rating_feedbacks(file_path: str) -> list[dict]:
    # Открываем файл в формате .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    product_data = []

    try:
        for url in urls_list:

            print(f'Обрабатывается: {url}')

            try:
                driver.get(url=url)
                time.sleep(randint(3, 5))
            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            html = driver.page_source

            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                try:
                    driver.get(url=f"{url}&page={page}")
                    time.sleep(randint(3, 5))
                except Exception as ex:
                    print(f'{url}: {ex}')
                    continue

                html = driver.page_source

                soup = BeautifulSoup(html, 'lxml')

                data_items = soup.find('div', class_='x6i').find_all('div', class_='iv4')

                print(f'Всего: {len(data_items)} продуктов на {page} странице!')

                for item in data_items:
                    try:
                        url_product = f"https://www.ozon.ru{item.find('a').get('href')}"
                    except Exception:
                        url_product = ''
                    try:
                        rating = item.find('div', class_='t8 t9 u tsBodyMBold').text.split()[0]
                    except Exception:
                        rating = ''
                    try:
                        feedbacks_count = item.find('div', class_='t8 t9 u tsBodyMBold').text.split()[1]
                    except Exception:
                        feedbacks_count = ''

                    product_data.append(
                        {
                            'url': url_product,
                            'rating': rating,
                            'feedbacks_count': feedbacks_count
                        }
                    )

        return product_data

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

# Функция получения данных с карточки продукта
def get_data_products_ozone(product_data: list) -> list[dict]:

    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    result_list = []

    try:
        for item in product_data[:10]:
            try:
                driver.get(url=item['url'])
                time.sleep(randint(3, 5))
                # driver.execute_script("window.scrollTo(0, 4000);")
                # time.sleep(randint(3, 5))
                # driver.execute_script("window.scrollTo(4000, 8000);")
                # time.sleep(randint(8, 10))
            except Exception as ex:
                print(f"get_data: {item['url']} - {ex}")
                continue

            html = driver.page_source


            soup = BeautifulSoup(html, 'lxml')

            try:
                name = soup.find('div', {'data-widget': 'webProductHeading'}).find('h1').text.strip()
            except Exception:
                name = None
            try:
                brand = soup.find('a', class_='qj7').text.strip()
            except Exception:
                brand = None
            try:
                id_product = soup.find('div', {'data-widget': 'webDetailSKU'}).text.strip()
            except Exception:
                id_product = None
            try:
                color = soup.find('span', string=re.compile('Цвет:')).find_next().text.strip()
            except Exception:
                color = None

            try:
                item_price = soup.find('div', {'data-widget': 'webPrice'})
            except Exception:
                item_price = None
            try:
                sale_price = ''.join(filter(lambda x: x.isdigit(), item_price.find('span', string=re.compile(
                    'без Ozon Карты')).find_previous().find_previous().find_previous().text))
            except Exception:
                sale_price = None
            try:
                ozone_price = ''.join(filter(lambda x: x.isdigit(), item_price.find('span', string=re.compile(
                    'c Ozon Картой')).find_parent().text))
            except Exception:
                ozone_price = None

            result_list.append(
                {
                    'Ozone': 'Ozone',
                    'Ссылка': item.get('url'),
                    'Бренд': brand,
                    'Название': name,
                    'SKU': id_product,
                    'Цвет': color,
                    'РЦ+СПП': sale_price,
                    'Рейтинг': item.get('rating'),
                    'Кол-во отзывов': item.get('feedbacks_count'),
                    'Цена с Ozone картой': ozone_price
                }
            )

        return result_list

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

# Функция для записи данных в формат xlsx
def save_excel_ozone(data: list) -> None:
    if not os.path.exists('data'):
        os.makedirs('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='Ozone', index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')

def main():
    product_data = get_urls_rating_feedbacks(file_path='data/urls_list_ozone.txt')
    ozone_data = get_data_products_ozone(product_data=product_data)
    save_excel_ozone(data=ozone_data)

    execution_time = datetime.now() - start_time
    print('Сбор данных Ozone завершён!')
    print(f'Время работы программы: {execution_time}')



if __name__ == '__main__':
    main()
