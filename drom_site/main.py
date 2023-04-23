import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import os
import csv

start_time = datetime.now()

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}
# headers = {
#     'accept': '*/*',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
#                   'Safari/537.36'
# }

region = '77'


# region = 'region77'
# brand = 'kia'
# page = 'page100'
# url = f"https://auto.drom.ru/{region}/{brand}/all/{page}/"

def get_urls(headers):
    url_list = []

    with requests.Session() as session:
        for i in range(1, 101):
            try:
                url = f"https://auto.drom.ru/region{region}/all/page{i}/"
                response = session.get(url=url, headers=headers)

                soup = BeautifulSoup(response.text, 'lxml')

                urls_page = soup.find(class_='css-1nvf6xk eojktn00').find('div').find_all('a')

            except Exception as ex:
                print(ex)
                continue

            for item in urls_page:
                url = item.get('href')
                url_list.append(url)

            print(i)

        with open(f'data/url_list_{region}.txt', 'w', encoding='utf-8') as file:
            print(*url_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        url_list = [line.strip() for line in file.readlines()]

    service = Service(executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe")

    options = Options()
    # options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    #                      ' Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    browser = webdriver.Chrome(service=service,
                               executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
                               options=options)
    browser.maximize_window()

    try:
        for i, url in enumerate(url_list[:10], 1):
            try:
                browser.implicitly_wait(5)
                browser.get(url=url)
            except Exception as ex:
                print(ex)
                continue
            try:
                if browser.find_elements(By.CSS_SELECTOR, 'button[data-ga-stats-name=show_full_description]'):
                    browser.find_element(By.CSS_SELECTOR, 'button[data-ga-stats-name=show_full_description]').click()
                button_phone = browser.find_element(By.CSS_SELECTOR, 'button[data-ftid=open-contacts]')
                button_phone.click()
            except Exception as ex:
                print(ex)
            try:
                # phone = WebDriverWait(browser, 5).until(
                #     EC.text_to_be_present_in_element((By.CLASS_NAME, 'e1i7tubr0'), '+7')
                # )
                browser.implicitly_wait(5)
                phone = browser.find_element(By.CLASS_NAME, "e1i7tubr0").text.strip()
            except Exception as ex:
                phone = None
            soup = BeautifulSoup(browser.page_source, 'lxml')
            try:
                title = soup.find(class_='css-1kb7l9z e162wx9x0').text.strip()
            except Exception:
                title = None
            try:
                price = soup.find(class_='css-eazmxc e162wx9x0').text.replace('\u20bd', ' ').strip()
            except Exception:
                price = None
            try:
                date = soup.find(class_='css-pxeubi evnwjo70').text.strip()
            except Exception:
                date = None
            try:
                dealer_name = soup.select_one('[data-ga-stats-name=dealer_name]').text.strip()
            except Exception:
                dealer_name = None
            try:
                description = ' '.join(
                    soup.find(class_='css-1j8ksy7 eotelyr0').text.replace('\U0001f4a1', ' ').replace('\u2757',
                                                                                                     ' ').replace(
                        '\U0001f525', ' ').replace('\U0001f381', ' ').replace('\u2714', ' ').strip().split())
            except Exception:
                description = None
            try:
                city = description.split()[-1]

            except Exception:
                city = None

            if not os.path.exists('data'):
                os.mkdir('data')

            with open(f'data/data_{region}.csv', 'a', encoding='cp1251', newline='') as file:
                writer = csv.writer(file, delimiter=';')

                writer.writerow(
                    (
                        url,
                        title,
                        price,
                        date,
                        phone,
                        dealer_name,
                        city,
                        description
                    )
                )
            print(i)


    except Exception as ex:
        print(ex)

    finally:
        browser.close()
        browser.quit()


def main():
    get_urls(headers=headers)
    get_data(f'data/url_list_{region}.txt')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
