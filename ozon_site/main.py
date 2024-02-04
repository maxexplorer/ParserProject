import time

from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import openpyxl


# Открываем файл Excel
workbook = openpyxl.load_workbook("D:/PycharmProjects/ParserProject/ozon_site/data/table.xlsx")

# Выбираем активный лист (или любой другой лист)
ws = workbook.active

def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()
    # driver.set_page_load_timeout(15)
    driver.implicitly_wait(15)

    try:
        for row in ws.iter_rows(min_row=4):
            for cell in row:
                if cell.hyperlink is not None:
                    # print(f'row {cell.row}: {cell.hyperlink.target}')

                    try:
                        driver.get(url=cell.hyperlink.target)
                        time.sleep(5)

                        soup = BeautifulSoup(driver.page_source, 'lxml')
                    except Exception as ex:
                        print(ex)
                        continue

                    try:
                        out_of_stock = soup.find('h2', class_='yk5').text.strip()
                        if 'Этот товар закончился' == out_of_stock:
                            continue
                    except Exception as ex:
                        pass

                    try:
                        price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='ol2 o0l').text))
                    except Exception as ex:
                        print(f'price - {ex}')
                        price = ''

                    try:
                        stor_item = soup.find('span', class_='ia1').find_next().find_next().find_next().text
                        storage = 'FBO' if 'Со склада Ozon' in stor_item else 'FBS'
                    except Exception as ex:
                        print(f'storage - {ex}')
                        storage = ''

                    try:
                        add_in_basket = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div[2]/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
                        add_in_basket.click()

                        WebDriverWait(driver, 15).until(
                            EC.text_to_be_present_in_element((By.XPATH,
                                                              '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button/div[1]/div/span[1]'),
                                                             'В корзине')
                        )

                        in_basket = driver.find_element(By.XPATH,
                                                        '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')
                        in_basket.click()
                    except Exception as ex:
                        print(ex)
                        pass

                    try:
                        quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode = numeric]').get_attribute('max')
                    except Exception as ex:
                        print(f'quantity - {ex}')
                        quantity = ''

                    time.sleep(5)

                    try:
                        button_del1 = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[1]/div/div/div[1]/div[1]/button')

                        button_del1.click()

                        button_del2 = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[2]/div/div/section/div[3]/button'))
                        )

                        button_del2.click()
                    except Exception as ex:
                        print(ex)
                        pass

                    print(price, storage, quantity)

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
