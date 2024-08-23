import time
from datetime import datetime
import os
from random import randint
import csv
import re
import json

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions

from bs4 import BeautifulSoup

start_time = datetime.now()


# Функция инициализации объекта chromedriver
def init_undetected_chromedriver(headless_mode=False):
    if headless_mode:
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = undetectedChrome(options=options)
        driver.implicitly_wait(15)
    else:
        driver = undetectedChrome()
        driver.maximize_window()
        driver.implicitly_wait(15)
    return driver


# Функция получения количества страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 27

    return pages


# Функция получения ссылок товаров
def get_products_urls(driver: undetectedChrome, brand: str, seller: str):
    pages = 27

    for page in range(1, 27):
        products_urls = []
        page_url = f"https://www.ozon.ru/brand/apple-26303000/?page={page}&seller=0"
        try:
            driver.get(url=page_url)
            time.sleep(3)
            html = driver.page_source
        except Exception as ex:
            print(f"{page_url} - {ex}")
            continue

        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')

        try:
            data_items = soup.find('div', class_='widget-search-result-container').find_all('div', class_='tile-root')
        except Exception as ex:
            print(f'data_items: {page_url} - {ex}')
            continue

        for item in data_items:
            try:
                product_url = f"https://www.ozon.ru{item.find('a').get('href')}"
            except Exception:
                product_url = ''

            products_urls.append(product_url)

        print(f'Обработано: {page}/{pages} страниц')

        if not os.path.exists('data'):
            os.makedirs('data')

        with open(f'data/products_urls_list_{brand}_{seller}.txt', 'a', encoding='utf-8') as file:
            print(*products_urls, file=file, sep='\n')


# Функция получения данных товаров
def get_products_data(driver: undetectedChrome, products_urls_list: list, brand: str, seller: str) -> None:
    result_list = []
    batch_size = 10

    for product_url in products_urls_list[:100]:
        try:
            driver.get(url=product_url)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 4000);")
            time.sleep(2)
            html = driver.page_source
        except Exception as ex:
            print(f"{product_url} - {ex}")
            continue

        if not html:
            print(f'not html: {product_url}')
            continue

        with open('data/index.html', 'r', encoding='utf-8') as file:
            html = file.read()

        soup = BeautifulSoup(html, 'lxml')

        # sript = soup.find('script', {"type":"application/ld+json"}).text

        try:
            category = soup.find('div', {'data-widget': 'breadCrumbs'}).find_all('li')[-1].text.strip()
        except Exception:
            category = None

        try:
            name = soup.find('div', {'data-widget': 'webProductHeading'}).find('h1').text.strip()
        except Exception:
            name = None

        try:
            article = ''.join(
                filter(lambda x: x.isdigit(), soup.find('button', {'data-widget': 'webDetailSKU'}).text.strip()))
        except Exception:
            article = None

        try:
            price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', string=re.compile(
                'без Ozon Карты')).find_parent().find_parent().find('span').text))
        except Exception:
            price = None

        try:
            images_urls_list = []
            images_items = soup.find('div', {'data-widget': 'webGallery'}).find_all('div', class_='km2_27')
            for image_item in images_items:
                image_url = image_item.find('img').get('src').replace('wc50', 'wc1000')
                images_urls_list.append(image_url)
            images_urls = '; '.join(images_urls_list)
        except Exception:
            images_urls = None

        try:
            description = soup.find('div', id='section-description').text.strip()
        except Exception:
            description = None

        try:
            characteristics = ''
            for item in soup.find('div', id='section-characteristics').find_all('dl'):
                dt = item.find('dt').text.strip()
                dl = item.find('dd').text.strip()
                characteristics += f'{dt}: {dl}; '
        except Exception:
            characteristics = None

        result_list.append(
            (
                brand,
                category,
                name,
                article,
                price,
                images_urls,
                description,
                characteristics,
            )
        )

        # Записываем данные в Excel каждые 1000 URL
        if len(result_list) >= batch_size:
            save_csv(data=result_list, brand=brand, seller=seller)
            result_list.clear()  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_csv(data=result_list, brand=brand, seller=seller)


# Функция для записи данных в формат csv
def save_csv(data: list, brand: str, seller: str) -> None:
    directory = 'data/results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{brand}_{seller}.csv'

    # Если файл не существует, записываем заголовки
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                    'brand: Бренд',
                    'category: Категория',
                    'name: Название',
                    'article: Артикул',
                    'price: Цена',
                    'images_urls: Изображения',
                    'description: Описание',
                    'characteristics: Характеристики',
                )
            )

    # Записываем данные в файл (добавляем строки)
    with open(file_path, 'a', encoding="utf-8-sig", newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(data)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    brand = 'Apple'
    seller = 'Ozon'

    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        # get_products_urls(driver=driver, brand=brand, seller=seller)
        with open('data/products_urls_list_Apple_Ozon.txt', 'r', encoding='utf-8') as file:
            products_urls_list = [line.strip() for line in file]
        get_products_data(driver=driver, products_urls_list=products_urls_list, brand=brand, seller=seller)
    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
