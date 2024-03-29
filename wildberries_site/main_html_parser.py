import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import json
import csv
from pandas import DataFrame, ExcelWriter
import openpyxl

brand = 'samsung'
page = 1

url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"

def get_html(url):
    options = Options()
    options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/108.0.0.0 Safari/537.36')
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")

    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options
    )

    try:
        browser.get(url=url)
        time.sleep(5)

        last_height = browser.execute_script("return document.body.scrollHeight")

        while True:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")
            # time.sleep(5)
            browser.implicitly_wait(10)
            # WebDriverWait(browser, 5).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, 'product-card-list'))
            # )
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = browser.page_source
        return html
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        brand_count = soup.find('span', class_='goods-count').text
        pages = int(''.join((c for c in brand_count if c.isdigit()))) // 100 + 1
        return pages
    except Exception as ex:
        print(ex)


def get_content(html):
    cards = []
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_="product-card")
    for item in items:
        try:
            title = item.find('span', class_='goods-name').text.strip(' / ')
        except Exception:
            title = 'Нет названия'
        try:
            lower_price = int(item.find(class_='price__lower-price').text.strip().replace('\xa0', '').replace('₽', ''))
        except Exception:
            lower_price = 'Нет цены'
        try:
            price = int(
                item.find('span', class_='price__wrap').find('del').text.strip().replace('\xa0', '').replace('₽', ''))
        except Exception:
            price = 'Нет цены'
        try:
            card_discount = item.find('span', class_='product-card__tip').text.strip()
            discount = int(''.join((c for c in card_discount if c.isdigit())))
        except Exception:
            discount = 'Нет скидки'
        try:
            rating = int(item.find('span', class_='product-card__rating').get('class')[-1][-1])
        except:
            rating = 'Нет рейтинга'
        try:
            url = item.find('a', class_='product-card__main j-card-link').get('href')
        except:
            url = 'Нет ссылки на товар'

        cards.append(
            {
                'brand': brand.title(),
                'title': title,
                'lower_price': lower_price,
                'price': price,
                'discount': discount,
                'rating': rating,
                'url': url
            }
        )
    return cards


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print('Данные сохранены в файл "data.json"')


def save_csv(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ('Брэнд',
             'Наименование',
             'Цена со скидкой',
             'Цена без скидки',
             'Скидка',
             'Рейтинг',
             'Ссылка на карточку товара')
        )

    with open('data/data.csv', 'a', encoding='utf-8') as file:
        for item in data:
            writer = csv.writer(file)
            writer.writerow(
                (item['brand'],
                 item['title'],
                 item['lower_price'],
                 item['price'],
                 item['discount'],
                 item['rating'],
                 item['url'])
            )
            # [*(v.values() for v in data)]
    print('Данные сохранены в файл "data.csv"')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)
    newdataframe = dataframe.rename(columns={'brand': 'Брэнд', 'title': 'Наименование',
                                             'lower_price': 'Цена со скидкой', 'price': 'Цена без скидки',
                                             'discount': 'Скидка', 'rating': 'Рейтинг',
                                             'url': 'Ссылка на карточку товара'
                                             })
    writer = ExcelWriter('data/data.xlsx')
    newdataframe.to_excel(writer, 'data')
    writer.save()
    print('Данные сохранены в файл "data.xlsx')


def parse(url):
    html = get_html(url)
    pages = get_pages(html)
    print(f'Количество страниц: {pages}')
    cards = []
    pages = int(input('Введите количество страниц: '))
    for page in range(1, pages + 1):
        print(f'Парсинг страницы: {page}')
        url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"
        html = get_html(url)
        cards.extend(get_content(html))
    save_json(cards)
    save_csv(cards)
    save_excel(cards)


if __name__ == '__main__':
    parse(url=url)
