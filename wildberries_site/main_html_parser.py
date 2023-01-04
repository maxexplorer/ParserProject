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

url = f"https://www.wildberries.ru/brands/{brand}/"


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

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/page_source.html', 'w', encoding='utf-8') as file:
            file.write(browser.page_source)
    except Exception as ex:
        print(ex)

    finally:
        browser.close()
        browser.quit()


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')

    try:
        brand_count = soup.find('div', class_='brand-custom-header')
        print(brand_count)
    except Exception as ex:
        print(ex)


def parse():
    get_html(url=url)



if __name__ == '__main__':
    parse()
