import json
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

import requests

# start_time = datetime.now()

# Открываем файл Excel
workbook = openpyxl.load_workbook("data/table_1.xlsx")

# # Выбираем активный лист (или любой другой лист)
# ws = workbook.active


# ws = workbook['Лист1']


def ozone_parser(workbook):
    # Выбираем активный лист (или любой другой лист)
    ws = workbook['ОЗОН']

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
                            row[cell.column - 4].value = ''
                            row[cell.column - 3].value = ''
                            row[cell.column - 2].value = 'Этот товар закончился'
                            continue
                    except Exception:
                        pass

                    try:
                        no_such_page = soup.find('h2', string=re.compile('Такой страницы не существует'))
                        if no_such_page:
                            row[cell.column - 4].value = ''
                            row[cell.column - 3].value = ''
                            row[cell.column - 2].value = 'Такой страницы не существует'
                            continue
                    except Exception:
                        pass

                    try:
                        price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='o3l lo2').text))
                        if not price:
                            price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='ol8 o8l pl2').text))

                    except Exception as ex:
                        # print(f'price - {ex}')
                        price = None

                    try:
                        stor_item = soup.find('span', class_='ai2').text.strip()
                        storage = 'FBO' if 'Со склада Ozon' in stor_item else 'FBS'
                    except Exception as ex:
                        # print(f'storage - {ex}')
                        storage = None

                    try:
                        add_in_basket = driver.find_element(By.XPATH,
                                                            '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[1]/button')

                        add_in_basket.click()
                    except Exception as ex:
                        # print(f'add_in_basket: {ex}')
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
                        # print(f'in_basket: {ex}')
                        continue

                    try:
                        quantity = driver.find_element(By.CSS_SELECTOR, 'input[inputmode=numeric]').get_attribute(
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
                        # print(f'button_del1: {ex}')
                        continue

                    try:
                        button_del2 = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '/html/body/div[3]/div/div[2]/div/div/section/div[3]/button'))
                        )
                        button_del2.click()
                    except Exception as ex:
                        # print(f'button_del2: {ex}')
                        continue

                    row[cell.column - 4].value = price
                    row[cell.column - 3].value = quantity
                    row[cell.column - 2].value = storage

                    # print(f'{cell.hyperlink.target}: price-{price}, quantity-{quantity}, storage-{storage}')

    except Exception as ex:
        print(ex)
    finally:
        workbook.save('data/result_table.xlsx')
        driver.close()
        driver.quit()


def wildberries_parser(workbook):
    # Выбираем активный лист (или любой другой лист)
    ws = workbook['ВБ']

    c = 1

    for row in ws.iter_rows(min_row=4):
        for cell in row:
            if cell.hyperlink is not None:
                url = cell.hyperlink.target
                prod_id = url.split('catalog')[-1].split('detail')[0].strip('/')


    #
    # headers = {
    #     'Accept': '*/*',
    #     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    #     'Connection': 'keep-alive',
    #     'Origin': 'https://www.wildberries.ru',
    #     'Referer': 'https://www.wildberries.ru/catalog/18172488/detail.aspx',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'cross-site',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    #     'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    #
    # params = {
    #     'appType': '1',
    #     'curr': 'rub',
    #     'dest': '-1257786',
    #     'spp': '30',
    #     'nm': '18172488',
    # }
    #
    # response = requests.get('https://card.wb.ru/cards/v1/detail', params=params, headers=headers)
    #
    # print(response.status_code)



    # with open('data/wb_res.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    # with open('data/wb_res.json', 'r', encoding='utf-8') as file:
    #     data = json.load(file)
    #
    #
    # print(data['data']['products'][0]['salePriceU'])
    # print(data['data']['products'][0]['sizes'][0]['stocks'][0]['qty'])
    #


def main():
    wildberries_parser(workbook=workbook)

    # execution_time = datetime.now() - start_time
    # print('Сбор данных завершен!')
    # print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
