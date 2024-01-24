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
    driver.implicitly_wait(15)

    try:
        driver.get(url="https://ozon.ru/t/601oMbY")

        # basket = driver.find_element(By.CSS_SELECTOR, 'div.j0s')

        # print(basket)

        basket = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.j0s'))
        )



        basket.click()



        #
        # WebDriverWait(driver, 15).until(
        #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#layoutPage > div.b0 > div.container.b4 > div.kq7.r1k > div.kq7.r2k.rk.kr0 > div.kq7.r2k.rk.k0r > div.ql1.q3l > div > div.q2l > div > div > div.j0s > div > div > div > div.d4153-a.jr9 > button > div.b235-a'), 'В корзине')
        # )
        #
        # in_basket = driver.find_element(By.CSS_SELECTOR, '#layoutPage > div.b0 > div.container.b4 > div.kq7.r1k > div.kq7.r2k.rk.kr0 > div.kq7.r2k.rk.k0r > div.ql1.q3l > div > div.q2l > div > div > div.j0s > div > div > div > div.d4153-a.jr9 > button > div.b235-a')
        # in_basket.click()
        #
        #
        # quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode = numeric]').get_attribute('max')
        #
        # print(quantity)


        # button_del = driver.find_element(By.CSS_SELECTOR, '#layoutPage > div.b0 > div > div > div.container.b4 > div:nth-child(5) > div.d6.c7 > div > div > div.l8b > div.bl9 > button')
        # # button_del = driver.find_element(By.CSS_SELECTOR, 'button.mb bm0 ga26-a undefined')
        #
        # button_del.click()
        #
        # time.sleep(10)

        # delete = driver.find_element(By.CSS_SELECTOR, 'button.b235-a0 b235-b5')

        #
        # if not os.path.exists('data'):
        #     os.makedirs('data')
        #
        # with open('data/page_source.html', 'w', encoding='utf-8') as file:
        #     file.write(driver.page_source)

        # time.sleep(5)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

def get_data():
    pass

def main():
    undetected_chromdriver()


if __name__ == '__main__':
    main()
