import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json

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

        # if not os.path.exists('data'):
        #     os.mkdir('data')
        #
        # with open('data/page_source.html', 'w', encoding='utf-8') as file:
        #     file.write(browser.page_source)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()

    html = browser.page_source
    return html


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        brand_count = soup.find('span', class_='brand-custom-header__count').text
        pages = int(''.join((c for c in brand_count if c.isdigit()))) // 100 + 1
    except Exception:
        pages = 1
    return pages

def get_content(html):
    pass


def parse():
    # html = get_html(url=url)
    with open('data/page_source.html', 'r', encoding='utf-8') as file:
        html = file.read()
    pages = get_pages(html)
    print(f'Количество страниц: {pages}')
    cards = []
    pages = int(input('Введите количество страниц: '))
    for page in range(1, pages + 1):
        print(f'Парсинг страницы: {page}')
        url = f"https://www.wildberries.ru/brands/{brand}?sort=popular&page={page}"
        html = get_html(url)
        cards.extend(get_content(html))







if __name__ == '__main__':
    parse()
