import json
import re
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

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
        time.sleep(5)
        html = browser.page_source

    except Exception as ex:
        raise UnboundLocalError("html not received")

    finally:
        browser.close()
        browser.quit()

    if not os.path.exists('data'):
        os.makedirs('data')

    # with open('data/html_data.txt', 'w', encoding='utf-8') as file:
    #     file.write(html)

    return html


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find_all('span', class_='styles-module-text-InivV')[-1].text)
    except Exception:
        pages = 1
    return pages


def get_data(url_list):
    seller_info_list = []

    for category_url in url_list[:1]:
        html = browser(url=category_url)
        pages = get_pages(html=html)
        for page in range(1, pages + 1):
            product_url = f"{category_url}?p={page}"
            html = browser(url=product_url)

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
                    seller_id = item.find('a', target='_blank').get('href').split('/')[-2]
                except Exception:
                    seller_id = None

                seller_info_list.append(
                    {
                        'title': title,
                        'id_seller': seller_id
                    }
                )
            print(f'Processed: {page} page!!!')

    with open('data/json_data.json', 'w', encoding='utf-8') as file:
        json.dump(seller_info_list, file, indent=4, ensure_ascii=False)

def get_feedback(seller_info_list):
    feedback_list = []

    limit = 25
    offset = 0

    for id in seller_info_list:
        seller_url = f"https://www.avito.ru/web/5/user/{id}/ratings?limit={limit}&offset={offset}&sortRating=date_desc&summary_redesign=1"

        html = browser(url=seller_url)

        soup = BeautifulSoup(html, 'lxml')

        json_data = soup.find('pre').text
        dict_data = json.loads(json_data)['entries']

        for item in dict_data:
            if 'textSections' in item['value']:
                title = item.get('value').get('title')
                itemTitle = item.get('value').get('itemTitle')
                text = item.get('value').get('textSections')[0].get('text')

                print(f"{title}|||{title}|||{text}")

                feedback_list.append(
                    {
                        'title': title,
                        'itemTitle': itemTitle,
                        'text': text
                    }
                )


def main():
    get_data(url_list=url_list)

    # with open('data/html_data.txt', 'r', encoding='utf-8') as file:
    #     html = file.read()


if __name__ == '__main__':
    main()
