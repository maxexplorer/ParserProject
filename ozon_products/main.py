import time
from datetime import datetime
import os
from random import randint
import re

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

from new_undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


# Функция получения ссылок товаров
def get_products_urls(driver: undetectedChrome):
    pages = 100
    products_urls = []

    for page in range(1, pages + 1):
        page_url = f"https://www.ozon.ru/brand/teyes-87208738/?currency_price=15000.000%3B196086.000&text=cc3&page={page}"
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
            data_items = soup.find('div', {'data-widget': 'tileGridDesktop'}).find_all('div',
                                                                                       class_='tile-root u4i_25 kj4_25 kj5_25')
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

    directory = 'data'

    os.makedirs(directory, exist_ok=True)

    with open(f'{directory}/product_urls_list.txt', 'a', encoding='utf-8') as file:
        print(*products_urls, file=file, sep='\n')


# Функция получения данных товаров
def get_products_data(driver: undetectedChrome, product_urls_list: list, brand: str) -> None:
    result_list = []
    batch_size = 100

    count_products = len(product_urls_list)

    for i, product_url in enumerate(product_urls_list, 1):
        try:
            driver.get(url=product_url)

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-widget="webProductHeading"]')
                )
            )
            scroll_and_wait(driver)
            html = driver.page_source
        except Exception as ex:
            print(f"{product_url} - {ex}")
            continue

        if not html:
            print(f'not html: {product_url}')
            continue

        soup = BeautifulSoup(html, 'lxml')

        try:
            out_of_stock = soup.find('h2', string=re.compile('Этот товар закончился'))
            if out_of_stock:
                print(f'{product_url}: Этот товар закончился')
                continue
        except Exception:
            pass

        try:
            no_such_page = soup.find('h2', string=re.compile('Такой страницы не существует'))
            if no_such_page:
                print(f'{product_url}: Такой страницы не существует')
                continue
        except Exception:
            pass

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
            discount_price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', string=re.compile(
                'c Ozon Картой')).find_parent().text))
        except Exception as ex:
            discount_price = None

        if not price:
            continue

        try:
            image_urls_list = []
            images_items = soup.find('div', class_='pdp_as7').find_all('div', class_='pdp_e1a')
            for image_item in images_items:
                image_url = image_item.find('img').get('src')
                image_url = re.sub(r'wc\d+', 'wc1000', image_url)
                image_urls_list.append(image_url)
            images_urls = ' | '.join(image_urls_list)
        except Exception:
            images_urls = None

        try:
            description = ''
            description_items = soup.find_all('div', id='section-description')
            for description_item in description_items:
                try:
                    text = description_item.find('div', class_='RA-a1').text.strip()
                except Exception:
                    continue
                description += text
        except Exception:
            description = None

        try:
            characteristics = ''
            characteristic_items = soup.find('div', id='section-characteristics').find_all('dl')
            for characteristic_item in characteristic_items:
                dt = characteristic_item.find('dt').text.strip()
                dd = characteristic_item.find('dd').text.strip()
                characteristics += f'{dt}: {dd}; '
        except Exception:
            characteristics = None

        result_list.append(
            (
                {
                    'Бренд': brand,
                    'Категория': category,
                    'Название': name,
                    'Артикул': article,
                    'Цена без Ozon Карты': price,
                    'Цена c Ozon Картой': discount_price,
                    'Ссылка на изображения': images_urls,
                    'Описание': description,
                    'Характеристики': characteristics
                }
            )
        )

        print(f'ОБработано: {i}/{count_products}')

        # Записываем данные в CSV каждые batch_size
        if len(result_list) >= batch_size:
            save_excel(data=result_list, brand=brand)
            result_list.clear()  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_excel(data=result_list, brand=brand)


def scroll_and_wait(driver, pause=0.5, max_tries=10):
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_tries):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            return  # дальше не грузится

        last_height = new_height


def save_excel(data: list[dict], brand: str, sheet_name: str = 'Лист1') -> None:
    """
    Сохраняет данные в Excel-файл.

    - Если файл не существует — создает
    - Если существует — дописывает данные в конец

    :param data: Список словарей с данными
    :param sheet_name: Имя листа Excel
    """

    cur_date: str = datetime.now().strftime('%d-%m-%Y')

    directory: str = 'results'
    file_path: str = f'{directory}/result_data_{brand}_{cur_date}.xlsx'

    # Создаем директорию для результатов
    os.makedirs(directory, exist_ok=True)

    # Если файл отсутствует — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Читаем существующие данные
    df_existing: DataFrame = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows: int = len(df_existing.index)

    # Добавляем новые строки
    new_df: DataFrame = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows,
            header=(num_existing_rows == 0),
            sheet_name=sheet_name,
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_unique_urls(file_path: str) -> None:
    # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
    with open(file_path, 'r', encoding='utf-8') as file:
        unique_urls = set(line.strip() for line in file)

    # Сохраняем уникальные URL-адреса обратно в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        print(*unique_urls, file=file, sep='\n')


def main():
    brand = 'Teyes'
    file_path = 'data/product_urls_list.txt'

    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        get_products_urls(driver=driver)

        get_unique_urls(file_path=file_path)

        with open(file_path, 'r', encoding='utf-8') as file:
            product_urls_list = [line.strip() for line in file]
        get_products_data(driver=driver, product_urls_list=product_urls_list, brand=brand)
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
