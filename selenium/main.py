import time
from random import randint
import re

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

from bs4 import BeautifulSoup


useragent = UserAgent().random

def chromdriver():
    options = Options()
    options.add_argument(f"User-Agent={useragent}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # driver.set_page_load_timeout(15)

    try:
        driver.get(url="https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
        time.sleep(15)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()

    try:
        driver.get(url="https://ozon.ru/t/Z2b4LLK")
        time.sleep(5)
        try:
            add_in_basket = driver.find_element(By.XPATH, '//div[contains(text(), "Добавить в корзину")]')
            parent_element = add_in_basket.find_element(By.XPATH, "../..")
            parent_element.click()
        except Exception as ex:
            print(f'add_in_basket: {ex}')

        try:

            time.sleep(randint(3, 5))

            in_basket = driver.find_element(By.XPATH, '//span[contains(text(), "Корзина")]')

            in_basket.click()

            time.sleep(randint(3, 5))


        except Exception as ex:
            print(f'in_basket: {ex}')


        time.sleep(randint(3, 5))


    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def undetected_chromdriver_cloudflare():
    # options = webdriver.ChromeOptions()
    # is equivalent to
    options = Options()

    # options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    #                      ' Chrome/120.0.0.0 Safari/537.36')
    options.add_argument(f'User-Agent={useragent}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })

    try:
        driver.maximize_window()
        # driver.get(url="https://www.sneakersnstuff.com/")
        # driver.get(url="https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
        driver.get(url="https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
        time.sleep(30)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    # chromdriver()
    undetected_chromdriver()


if __name__ == '__main__':
    main()
