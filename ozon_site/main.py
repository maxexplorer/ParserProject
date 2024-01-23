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
    driver.implicitly_wait(15)

    try:
        driver.get(url="https://ozon.ru/t/601oMbY")

        basket = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ql1'))
        )

        basket.click()


        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div.ql1'), 'В корзине')
        )

        in_basket = driver.find_element(By.CSS_SELECTOR, '#layoutPage > div.b0 > div.container.b4 > div.q5k.rk0 > div.q5k.rk1.kq9.k9q > div.q5k.rk1.kq9.qk9 > div.l0q.ql2 > div > div.ql1 > div > div > div.rj9 > div > div > div > div.j4r > button > div.b235-a')
        in_basket.click()

        time.sleep(10)

        quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode = numeric]').get_attribute('max')

        print(quantity)





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
