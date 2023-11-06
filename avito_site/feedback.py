import json
import re
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

url = "https://www.avito.ru/web/5/user/3cca7b3710e1a0028e5a63044c141d56/ratings?limit=65&offset=65&sortRating=date_desc&summary_redesign=1"

url_list = [
    'https://www.avito.ru/all/telefony',
    'https://www.avito.ru/all/bytovaya_tehnika',
    'https://www.avito.ru/all/noutbuki'
]


def browser(url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")

    browser = webdriver.Chrome(options=options)

    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })
    # browser.implicitly_wait(10)
    browser.maximize_window()

    try:
        browser.get(url=url)
        time.sleep(15)
        html = browser.page_source

    except Exception as ex:
        print(ex)

    finally:
        browser.close()
        browser.quit()

    if not os.path.exists('data'):
        os.makedirs('data')

    # with open('data/html_data.txt', 'w', encoding='utf-8') as file:
    #     file.write(html)

    return browser, html


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find_all('span', class_='styles-module-text-InivV')[-1].text)
    except Exception:
        pages = 1
    return pages


def get_data(url_list):

    seller_url_list = []

    for url in url_list[:1]:
        _, html = browser(url=url)
        pages = get_pages(html=html)
        print(pages)

        # for page in range(1, pages + 1):
        for page in range(1, 2):
            url = f"{url}?p={page}"
            driver, html = browser(url=url)
            soup = BeautifulSoup(html, 'lxml')

            try:
                seller_info = soup.find_all('div', class_='style-root-uufhX')
            except Exception:
                seller_info = []

            for item in seller_info:
                try:
                    title = item.find('p').text
                except Exception:
                    title = None
                try:
                    url = item.find('a', target='_blank').get('href').split('/')[-2]
                except Exception:
                    url = None

                print(url, title)




        # soup = BeautifulSoup(html, 'lxml')
        #
        # json_data = soup.find('pre').text
        # dict_data = json.loads(json_data)['entries']
        #
        # for item in dict_data:
        #     if 'textSections' in item['value']:
        #         print(f"{item.get('value').get('title')}|||{item.get('value').get('itemTitle')}|||"
        #               f"{item.get('value').get('textSections')[0].get('text')}")
        #

def main():
    get_data(url_list=url_list)

    # with open('data/html_data.txt', 'r', encoding='utf-8') as file:
    #     html = file.read()



if __name__ == '__main__':
    main()
