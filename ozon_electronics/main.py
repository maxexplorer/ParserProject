import time
from datetime import datetime
import os
from random import randint

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions

from bs4 import BeautifulSoup

start_time = datetime.now()

# Создаём объект undetected_chromedriver
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

# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 27

    return pages


def get_products_urls(driver: undetectedChrome, brand: str, seller: str):
    pages = 27

    for page in range(1, pages + 1):
        products_urls = []
        page_url = f"https://www.ozon.ru/brand/apple-26303000/?page={page}&seller=0"
        try:
            driver.get(url=page_url)
            time.sleep(randint(1, 3))
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


def get_products_data():
    pass


def main():
    brand = 'Apple'
    seller = 'Ozon'

    driver = init_undetected_chromedriver(headless_mode=True)

    try:
        get_products_urls(driver=driver, brand=brand, seller=seller)
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

