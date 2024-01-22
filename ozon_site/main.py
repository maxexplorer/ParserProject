import os.path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome
from fake_useragent import UserAgent
import time



def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()

    driver = Chrome()
    driver.maximize_window()

    try:
        # driver.get(url="https://ozon.ru/t/601oMbY")
        driver.get(url="https://www.ozon.ru/cart")
        time.sleep(5)

        if not os.path.exists('data'):
            os.makedirs('data')

        with open('data/page_source.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    undetected_chromdriver()

if __name__ == '__main__':
    main()