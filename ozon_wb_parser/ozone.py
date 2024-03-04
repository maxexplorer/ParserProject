import json
import os
import re
import time
from random import randint

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# Функция получения количества страниц
def get_pages(html: str = None) -> int:
    try:
        soup = BeautifulSoup(html, 'lxml')

        pages = int(soup.find('div', class_='eo6').find_all('a')[-2].text)

        print(f'Всего: {pages} страниц!')
    except Exception:
        pages = 1

    return pages


# Функция полученя ссылок всех продуктов продавца
def get_urls(file_path: str) -> list:
    # Открываем файл в формате .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    # Создаем объект опций
    # options = ChromeOptions()
    # Включение фонового режима
    # options.add_argument('--headless')
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    product_data = []

    try:
        for url in urls_list[:1]:

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
                        feedbacks_count =item.find('div', class_='t8 t9 u tsBodyMBold').text.split()[1]
                    except Exception:
                        feedbacks_count = ''

                    product_data.append(
                        {
                            'url': url_product,
                            'rating': rating,
                            'feedbacks_count': feedbacks_count
                        }
                    )

                if not os.path.exists('data'):
                    os.makedirs('data')

                with open('data/data.json', 'w', encoding='utf-8') as file:
                    json.dump(product_data, file, indent=4, ensure_ascii=False)

        return product_data

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_data(file_path) -> list[dict]:
    # # Открываем файл в формате .txt
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     product_urls_list = [line.strip() for line in file.readlines()]
    #
    # # # Создаем объект опций
    # # # options = ChromeOptions()
    # # # Включение фонового режима
    # # # options.add_argument('--headless')
    # driver = Chrome()
    # driver.maximize_window()
    # driver.implicitly_wait(15)
    # # result_list = []
    # try:
    #     for url in product_urls_list[:1]:
    #         try:
    #             driver.get(url=url)
    #             time.sleep(randint(3, 5))
    #             # driver.execute_script("window.scrollTo(0, 4000);")
    #             # time.sleep(randint(3, 5))
    #             # driver.execute_script("window.scrollTo(4000, 8000);")
    #             # time.sleep(randint(8, 10))
    #         except Exception as ex:
    #             print(f'{url}: {ex}')
    #             continue
    #
    #         with open('data/product.html', 'w', encoding='utf-8') as file:
    #             file.write(driver.page_source)
    #
    #
    #
    # except Exception as ex:
    #     print(ex)
    # finally:
    #     driver.close()
    #     driver.quit()

    with open('data/product.html', 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'lxml')

    name = soup.find('div', {'data-widget': 'webProductHeading'}).find('h1').text.strip()
    id_product = soup.find('div', {'data-widget': 'webDetailSKU'}).text.strip()
    color = soup.find('span', string=re.compile('Цвет')).find_next().text.strip()
    item_price = soup.find('div', {'data-widget': 'webPrice'})

    sale_price = ''.join(filter(lambda x: x.isdigit(), item_price.find('span', string=re.compile(
        'без Ozon Карты')).find_previous().find_previous().find_previous().text))

    ozone_price = ''.join(filter(lambda x: x.isdigit(), item_price.find('span', string=re.compile(
        'c Ozon Картой')).find_parent().text))

    print(ozone_price)

    # product_url = ''
    #
    # result_list.append(
    #     {
    #         'Wildberries': 'Wildberries',
    #         'Ссылка': product_url,
    #         'Бренд': brand,
    #         'Название': name,
    #         'SKU': id_product,
    #         'Цвет': colors,
    #         'РЦ+СПП': sale_price,
    #         'Рейтинг': reviewRating,
    #         'Кол-во отзывов': count_feedbacks,
    #         'Последние 5 отзывов': average_rating,
    #         'Цена с WB кошельком': wb_price
    #     }
    # )


def main():
    product_data = get_urls(file_path='data/urls_list_ozone.txt')
    # ozone_data = get_data(file_path='data/product_urls_list.txt')


if __name__ == '__main__':
    main()
