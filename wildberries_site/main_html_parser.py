import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json
from pprint import pprint

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
        brand_count = soup.find('span', class_='brand-custom-header__count').text
        pages = int(''.join((c for c in brand_count if c.isdigit()))) // 100 + 1
    except Exception:
        pages = 1
    return pages


def get_content(html):
    cards = []
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('div', class_="product-card")
    for item in items:
        try:
            title = item.find('span', class_='goods-name').text
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
            card_sale = item.find('span', class_='product-card__sale').text.strip()
            sale = int(''.join((c for c in card_sale if c.isdigit())))
        except Exception:
            sale = 'Нет скидки'

        cards.append(
            {
                'title': title,
                'lower_price': lower_price,
                'price': price,
                'sale': sale
            }
        )
    return cards


def parse(url):
    html = get_html(url=url)
    pages = get_pages(html)
    print(f'Количество страниц: {pages}')
    cards = []
    pages = int(input('Введите количество страниц: '))
    for page in range(1, pages + 1):
        print(f'Парсинг страницы: {page}')
        url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"
        html = get_html(url)
        cards.extend(get_content(html))

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/cards.json', 'w', encoding='utf-8') as file:
        json.dump(cards, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parse(url=url)
