import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json
import csv
import pandas
from pandas import ExcelWriter
import openpyxl

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/108.0.0.0 Safari/537.36'
}
brand = 'samsung'
page = 1

# url = f"https://www.wildberries.ru/brands/{brand}/"
url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"


def get_html(url):
    options = Options()
    options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/108.0.0.0 Safari/537.36')

    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options
    )
    browser.maximize_window()

    try:
        browser.get(url=url)
        time.sleep(5)
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
            url_product = item.find('a', class_='product-card__main j-card-link').get('href')
        except:
            url_product = 'Нет ссылки на тоавар'

        cards.append(
            {
                'brand': brand.title(),
                'title': title,
                'lower_price': lower_price,
                'price': price,
                'discount': discount,
                'rating': rating,
                'url_product': url_product
            }
        )
    return cards


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


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
                 item['url_product'])
            )
            # [*(v.values() for v in data)]


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = pandas.DataFrame(data)
    newdataframe = dataframe.rename(columns={'brand': 'Брэнд', 'title': 'Наименование',
                                             'lower_price': 'Цена со скидкой', 'price': 'Цена без скидки',
                                             'discount': 'Скидка',
                                             })
    writer = ExcelWriter('data/data.xlsx')
    newdataframe.to_excel(writer, 'data')
    writer.save()
    print(f'Данные сохранены в файл "data.xlsx"')


def parse(url):
    # html = get_html(url)
    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(html)
    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    cards = get_content(html)
    # save_json(cards)
    # save_csv(cards)
    # save_excel(cards)
    # html = get_html(url)
    # pages = get_pages(html)
    # print(f'Количество страниц: {pages}')
    # cards = []
    # pages = int(input('Введите количество страниц: '))
    # for page in range(1, pages + 1):
    #     print(f'Парсинг страницы: {page}')
    #     url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"
    #     html = get_html(url)
    #     cards.extend(get_content(html))
    # save_excel(cards)
    # save_csv(cards)
    # save_json(cards)


if __name__ == '__main__':
    parse(url=url)
