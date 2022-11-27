import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import time

# url = "https://zoon.ru/msk/hotels/"
url = "https://rostov.zoon.ru/hotels/"

# options
options = webdriver.ChromeOptions()

# change useragent
useragent = UserAgent()
options.add_argument(f'user-agent={useragent.random}')


def get_search_html(url):
    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options,
    )
    browser.maximize_window()

    try:
        browser.get(url=url)
        time.sleep(5)

        while True:
            element = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'catalog-button-showMore'))
            )

            if not browser.find_elements(By.CLASS_NAME, 'js-next-page'):
                if not os.path.exists('data'):
                    os.mkdir('data')
                with open('data/page_source.html', 'w', encoding='utf-8') as file:
                    file.write(browser.page_source)
                break
            else:
                actions = ActionChains(browser)
                actions.move_to_element(element).click().perform()
                time.sleep(5)


    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


def get_items_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('div', class_='minicard-item__info')

    urls = []
    for item in items_divs:
        item_url = item.find('h2', class_='minicard-item__title').find('a').get('href')
        urls.append(item_url)

    with open('data/items_urls.txt', 'w', encoding='utf-8') as file:
        print(*urls, file=file, sep='\n')

    return '[INFO] Urls collected successfully!'


def main():
    get_search_html(url=url)
    print(get_items_urls(file_path='data/page_source.html'))


if __name__ == '__main__':
    main()
