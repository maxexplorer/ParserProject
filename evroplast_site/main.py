from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time
from datetime import datetime
import json
import csv
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

exceptions_list = []


def get_data(url_list):
    options = Options()
    # options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    #                      ' Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options
    )

    result_list = []
    try:
        for i, url in enumerate(url_list[:10], 1):
            try:
                browser.implicitly_wait(5)
                browser.get(url)
            except Exception:
                exceptions_list.append(url)
                continue
            try:
                title = browser.find_element(By.CLASS_NAME, "prod-info-main").text.strip()
            except Exception:
                title = None
            try:
                price = browser.find_element(By.CLASS_NAME, "prod-price").text.strip('RUB')
            except Exception:
                price = None
            try:
                parameters = ' '.join(browser.find_element(By.CLASS_NAME, "param-left-main").text.split())
            except Exception:
                parameters = None
            try:
                material = browser.find_element(By.CLASS_NAME, "prod-info-material").text
            except Exception:
                material = None
            try:
                analogue = browser.find_elements(By.CLASS_NAME, "prod-flex")
                if analogue:
                    url_analogue = analogue[0].get_attribute('href')
                else:
                    url_analogue = None
            except Exception:
                url_analogue = None
            try:
                if not browser.find_element(By.ID, "sechenie_img") and \
                        not browser.find_element(By.CLASS_NAME, "param-section-block"):
                    continue
                photo = browser.find_element(By.ID, "sechenie_img")
                photo.click()
                browser.implicitly_wait(3)
                time.sleep(1)
                browser.save_screenshot(f'data_img/{i}.png')
            except Exception:
                pass
            try:
                photo = browser.find_element(By.CLASS_NAME, "param-section-block")
                photo.click()
                browser.implicitly_wait(3)
                time.sleep(1)
                browser.save_screenshot(f'data_img/{i}.png')
            except Exception:
                pass

            result_list.append(
                {
                    'Название': title,
                    'Цена': price,
                    'Параметры': parameters,
                    'Материал': material,
                    'Ссылка': url,
                    'Ссылка аналога': url_analogue,
                    'Номер фото': f"{i}.png"
                }
            )

            print(f"Обработано {i} url")

    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()
    return result_list


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    # writer = ExcelWriter('data/data.xlsx', mode='w')
    # dataframe.to_excel(writer, sheet_name='data')
    # writer.save()
    # is equivalent to

    with ExcelWriter('data/data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    with open('data/url_list.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        lst_urls = list(reader)
    url_list = []
    for url in lst_urls:
        url_list.extend(url)
    url_list = [url.strip('; ') for url in url_list]
    with open('data/url_list.txt', 'w', encoding='utf-8') as file:
        print(*url_list, file=file, sep='\n')
    with open('data/url_list.txt', 'r', encoding='utf-8') as file:
        url_list = [line.strip() for line in file.readlines()]
    data = get_data(url_list=url_list)
    save_json(data)
    save_excel(data)
    if len(exceptions_list) > 0:
        with open('data/exceptions_list.txt', 'w', encoding='utf-8') as file:
            print(*exceptions_list, file=file, sep='\n')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
