import os
import re
import time
from datetime import datetime
from random import randint

from undetected_chromedriver import Chrome
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter

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


# Функция получения ссылок рейтинга, количества отзывов всех продуктов продавца
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

                data_items = soup.find('div', class_='widget-search-result-container').find_all('div', class_='tile-root')

                print(f'Всего: {len(data_items)} продуктов на {page} странице!')

                try:
                    brand = soup.find('span', class_='tsHeadline600Large').text.strip()
                except Exception:
                    brand = None

                for item in data_items:
                    try:
                        url_product = f"https://www.ozon.ru{item.find('a').get('href')}"
                    except Exception:
                        url_product = ''
                    try:
                        rating = item.find('div', class_='ai8 aj t3 t4 t5 tsBodyMBold').text.split()[0]
                    except Exception:
                        rating = ''
                    try:
                        feedbacks_count = item.find('div', class_='ai8 aj t3 t4 t5 tsBodyMBold').text.split()[1]
                    except Exception:
                        feedbacks_count = ''

                    product_data.append(
                        {
                            'url': url_product,
                            'brand': brand,
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
def get_data_products_ozon(product_data: list) -> list[dict]:
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    result_list = []

    try:
        for item in product_data:
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
                id_product = ''.join(
                    filter(lambda x: x.isdigit(), soup.find('span', {'data-widget': 'webDetailSKU'}).text.strip()))
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
                ozon_price = ''.join(filter(lambda x: x.isdigit(), item_price.find('span', string=re.compile(
                    'c Ozon Картой')).find_parent().text))
            except Exception:
                ozon_price = None

            result_list.append(
                {
                    'Ozon': 'Ozon',
                    'Ссылка': item.get('url'),
                    'Бренд': item.get('brand'),
                    'Название': name,
                    'SKU': id_product,
                    'Цвет': color,
                    'РЦ+СПП': sale_price,
                    'Рейтинг': item.get('rating'),
                    'Кол-во отзывов': item.get('feedbacks_count'),
                    'Цена с ozon картой': ozon_price
                }
            )

        return result_list

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

# Функция для записи данных в формат xlsx
def save_excel_ozon(data: list) -> None:
    if not os.path.exists('data/result_list.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='WB', index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name='ozon', index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')




