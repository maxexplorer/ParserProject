import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os

url = "https://www.avito.ru/all/odezhda_obuv_aksessuary/obuv_muzhskaya-ASgBAgICAUTeArqp1gI?cd=1"


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
    browser.maximize_window()

    try:
        browser.get(url=url)
        print(browser.window_handles)
        print(browser.current_url)
        # time.sleep(5)
        browser.implicitly_wait(5)

        items = browser.find_elements(By.CSS_SELECTOR, '[data-marker=item]')
        items[0].click()
        # time.sleep(5)

        browser.switch_to.window(browser.window_handles[1])
        print(browser.current_url)



        # html = browser.page_source
        # return html
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()
        time.sleep(5)


def get_content(html):
    soup = BeautifulSoup(html, 'lxml')

    items = soup.find_all('div', {'data-marker': 'item'})

    for item in items:
        title = item.find('h3', itemprop='name')
        print(title.text)


def main():
    html = get_html(url=url)
    # if not os.path.exists('data'):
    #     os.mkdir('data')
    # with open('data/index.html',  'w', encoding='utf-8') as file:
    #     file.write(html)
    # with open('data/index.html', 'r', encoding='utf-8') as file:
    #     html = file.read()
    # print(get_content(html))


if __name__ == '__main__':
    main()
