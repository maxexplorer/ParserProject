import time
import os
import re
from random import randint
from datetime import datetime

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter
import openpyxl

import pickle

start_time = datetime.now()

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/123.0.0.0 Safari/537.36'
}

district_urls = [
    "https://www.ddproperty.com/en/property-for-sale/1?district_code%5B0%5D=TH8404&freetext=Ko+Samui&search=true"
]


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


# Функция получения ссылокб рейтинга, количества отзывов всех продуктов продавца
def get_property_urls(district_urls: list) -> list[dict]:
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    property_urls_list = []

    try:
        for district_url in district_urls:

            print(f'Обрабатывается: {district_url}')

            try:
                driver.get(url=district_url)
                time.sleep(randint(3, 5))
            except Exception as ex:
                print(f'{district_url}: {ex}')
                continue

            html = driver.page_source

            pages = get_pages(html=html)

            print(f'Всего: {pages} страниц!')

            for page in range(1, pages + 1):
                try:
                    driver.get(
                        url=f"https://www.ddproperty.com/en/property-for-sale/{page}?district_code%5B0%5D=TH8404&freetext=Ko+Samui&search=true")
                    time.sleep(randint(3, 5))
                except Exception as ex:
                    print(f'page: {page} - {ex}')
                    continue

                html = driver.page_source

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    property_items = soup.find_all('div', class_='row listing-card__action-item')
                    for property_item in property_items:
                        property_url = property_item.find('a').get('href')
                        property_urls_list.append(property_url)
                except Exception as ex:
                    print(f'property_items: {ex}')
                    continue

                print(f'Обработано: {page}/{pages} страниц!')

        if not os.path.exists('data'):
            os.makedirs(f'data')

        with open(f'data/property_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*property_urls_list, file=file, sep='\n')

        return property_urls_list

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


# Функция получения данных с карточки продукта
def get_property_data(file_path: str) -> list[dict]:
    # Открываем файл в формате .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        property_urls_list = [line.strip() for line in file.readlines()]

    # options = ChromeOptions()
    # options.add_argument('--headless')
    #
    # driver = Chrome(options=options)

    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    result_list = []

    try:
        for property_url in property_urls_list[:1]:
            try:
                driver.get(url=property_url)
                time.sleep(randint(3, 5))

                input = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                print(input)

                input.click()

            except Exception as ex:
                print(f"property_url: {property_url} - {ex}")
                continue

            html = driver.page_source

            with open('data/index.html', 'w', encoding='utf-8') as file:
                file.write(html)

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                id_property = ''
            except Exception:
                id_property = ''

            result_list.append(
                {

                }
            )

        return result_list

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


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
    # get_property_urls(district_urls=district_urls)
    result_data = get_property_data(file_path='data/property_urls_list.txt')



    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
