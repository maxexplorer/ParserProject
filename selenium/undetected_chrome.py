import re
import time

from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()

    try:
        driver.get(url="https://ozon.ru/t/601oMbY")
        time.sleep(3)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    undetected_chromdriver()


if __name__ == '__main__':
    main()
