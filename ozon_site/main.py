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
    options = Options()
    # options.add_argument("--disable-blink-features=AutomationControlled")

    driver = Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url="https://ozon.ru/t/jYDXY4o")
        time.sleep(15)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    pass

if __name__ == '__main__':
    main()