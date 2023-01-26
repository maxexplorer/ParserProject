import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os


def get_html(url):
    options = Options()
    options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")

    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options
    )

    try:
        browser.get(url=url)
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()
        time.sleep(5)


def main():
    get_html(url="https://www.avito.ru/")


if __name__ == '__main__':
    main()
