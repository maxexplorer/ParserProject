import re
import time
from datetime import datetime
from random import randint

from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import openpyxl

start_time = datetime.now()

# Открываем файл Excel
workbook = openpyxl.load_workbook("D:/PycharmProjects/ParserProject/ozon_site/data/table.xlsx")

# Выбираем активный лист (или любой другой лист)
ws = workbook.active


def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    try:
        for row in ws.iter_rows(min_row=4):
            for cell in row:
                if cell.hyperlink is not None:
                    try:
                        driver.get(url=cell.hyperlink.target)
                        time.sleep(randint(3, 5))

                        soup = BeautifulSoup(driver.page_source, 'lxml')
                    except Exception as ex:
                        print(ex)
                        continue

                    try:
                        out_of_stock = soup.find('h2', string=re.compile('Этот товар закончился'))
                        if out_of_stock:
                            continue
                    except Exception:
                        pass

                    try:
                        no_such_page = soup.find('h2', string=re.compile('Такой страницы не существует'))
                        if no_such_page:
                            continue
                    except Exception:
                        pass

                    try:
                        price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='ol2 o0l').text))
                    except Exception as ex:
                        # print(f'price - {ex}')
                        price = None

                    try:
                        stor_item = soup.find('span', class_='ia1').find_next().find_next().find_next().text
                        storage = 'FBO' if 'Со склада Ozon' in stor_item else 'FBS'
                    except Exception as ex:
                        # print(f'storage - {ex}')
                        storage = None

                    try:
                        add_in_basket = driver.find_element(By.XPATH,
                                                            '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div[2]/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
                        add_in_basket.click()
                    except Exception as ex:
                        print(f'add_in_basket: {ex}')
                        continue

                    try:
                        WebDriverWait(driver, 15).until(
                            EC.text_to_be_present_in_element((By.XPATH,
                                                              '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button/div[1]/div/span[1]'),
                                                             'В корзине')
                        )

                        in_basket = driver.find_element(By.XPATH,
                                                        '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
                        in_basket.click()
                    except Exception as ex:
                        print(f'in_basket: {ex}')
                        continue

                    try:
                        quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode = numeric]').get_attribute(
                            'max')
                    except Exception as ex:
                        # print(f'quantity - {ex}')
                        quantity = None

                    time.sleep(5)

                    try:
                        button_del1 = driver.find_element(By.XPATH,
                                                          '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[1]/div/div/div[1]/div[1]/button')
                        button_del1.click()
                    except Exception as ex:
                        print(f'button_del1: {ex}')
                        continue

                    try:
                        button_del2 = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '/html/body/div[3]/div/div[2]/div/div/section/div[3]/button'))
                        )
                        button_del2.click()
                    except Exception as ex:
                        print(f'button_del2: {ex}')
                        continue

                    row[cell.column - 4].value = price
                    row[cell.column - 3].value = quantity
                    row[cell.column - 2].value = storage

                    print(price, quantity, storage, cell.hyperlink.target)

    except Exception as ex:
        print(ex)
    finally:
        workbook.save('data/table_result.xlsx')
        driver.close()
        driver.quit()


def get_data():
    pass


def main():
    undetected_chromdriver()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
