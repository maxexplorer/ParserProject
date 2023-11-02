import time

import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

url = "https://krisha.kz/prodazha/kvartiry/?das[house.year][to]=2023&das[price][from]=90000000&das[who]=1"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}




def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find_all('a', class_='paginator__btn')[-2].text.strip())
        return pages
    except Exception as ex:
        print(ex)


def get_phones(url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    try:
        browser.implicitly_wait(5)
        browser.get(url=url)
    except Exception as ex:
        print(ex)
    try:
        button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'show-phones')))
        button.click()
    except Exception as ex:
        print(ex)

def get_phone():
    import requests

    cookies = {
        'krishauid': '27a90cf7866809318956bbaf46bf1bee0566a1c3',
        '_gid': 'GA1.2.1622783382.1698864884',
        'ssaid': '1eb3cdf0-78e8-11ee-a9d4-ad9ab41bfaa8',
        '_ym_uid': '1698864885305000808',
        '_ym_d': '1698864885',
        '_ym_isad': '2',
        '_gcl_au': '1.1.628254214.1698864887',
        '_tt_enable_cookie': '1',
        '_ttp': 'z6CqOsq7az43qG0d1Q6z7yqkUep',
        '_fbp': 'fb.1.1698864889126.1219622591',
        '__gsas': 'ID=387fb42e7e2c73ba:T=1698864889:RT=1698864889:S=ALNI_MZYaWC_3MrfrarwirA-hbO66maZ9A',
        'tutorial': '%7B%22add-note%22%3A%22viewed%22%2C%22advPage%22%3A%22viewed%22%2C%22layoutPageContacts%22%3A%22viewed%22%7D',
        'hist_region': '2',
        'krssid': '1hmnc1jtddkmadcg645sodsvo8',
        '_ga_6YZLS7YDS7': 'GS1.1.1698936664.6.1.1698936664.60.0.0',
        '_ga': 'GA1.2.1691651900.1698864884',
        '_ym_visorc': 'b',
        'kr_cdn_host': '//alakt-kz.kcdn.online',
        '_gat': '1',
        '__tld__': 'null',
        '__gads': 'ID=fe861d45f5db215a:T=1698864883:RT=1698936666:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg',
        '__gpi': 'UID=00000cb0f49e709a:T=1698864883:RT=1698936666:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA',
        '_gat_UA-20095530-1': '1',
    }

    headers = {
        'authority': 'krisha.kz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'krishauid=27a90cf7866809318956bbaf46bf1bee0566a1c3; _gid=GA1.2.1622783382.1698864884; ssaid=1eb3cdf0-78e8-11ee-a9d4-ad9ab41bfaa8; _ym_uid=1698864885305000808; _ym_d=1698864885; _ym_isad=2; _gcl_au=1.1.628254214.1698864887; _tt_enable_cookie=1; _ttp=z6CqOsq7az43qG0d1Q6z7yqkUep; _fbp=fb.1.1698864889126.1219622591; __gsas=ID=387fb42e7e2c73ba:T=1698864889:RT=1698864889:S=ALNI_MZYaWC_3MrfrarwirA-hbO66maZ9A; tutorial=%7B%22add-note%22%3A%22viewed%22%2C%22advPage%22%3A%22viewed%22%2C%22layoutPageContacts%22%3A%22viewed%22%7D; hist_region=2; krssid=1hmnc1jtddkmadcg645sodsvo8; _ga_6YZLS7YDS7=GS1.1.1698936664.6.1.1698936664.60.0.0; _ga=GA1.2.1691651900.1698864884; _ym_visorc=b; kr_cdn_host=//alakt-kz.kcdn.online; _gat=1; __tld__=null; __gads=ID=fe861d45f5db215a:T=1698864883:RT=1698936666:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg; __gpi=UID=00000cb0f49e709a:T=1698864883:RT=1698936666:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA; _gat_UA-20095530-1=1',
        'referer': 'https://krisha.kz/a/show/667124453',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'alias': 'almaty/sevenhills',
    }

    response = requests.get('https://krisha.kz/complex/ajaxPhones', params=params, cookies=cookies, headers=headers)

    print(response.json())

    import requests

    cookies = {
        'krishauid': '27a90cf7866809318956bbaf46bf1bee0566a1c3',
        '_gid': 'GA1.2.1622783382.1698864884',
        'ssaid': '1eb3cdf0-78e8-11ee-a9d4-ad9ab41bfaa8',
        '_ym_uid': '1698864885305000808',
        '_ym_d': '1698864885',
        '_gcl_au': '1.1.628254214.1698864887',
        '_tt_enable_cookie': '1',
        '_ttp': 'z6CqOsq7az43qG0d1Q6z7yqkUep',
        '_fbp': 'fb.1.1698864889126.1219622591',
        '__gsas': 'ID=387fb42e7e2c73ba:T=1698864889:RT=1698864889:S=ALNI_MZYaWC_3MrfrarwirA-hbO66maZ9A',
        'tutorial': '%7B%22add-note%22%3A%22viewed%22%2C%22advPage%22%3A%22viewed%22%2C%22layoutPageContacts%22%3A%22viewed%22%7D',
        'hist_region': '2',
        'krssid': '1hmnc1jtddkmadcg645sodsvo8',
        '_ym_visorc': 'b',
        'kr_cdn_host': '//alakt-kz.kcdn.online',
        '_ym_isad': '2',
        '__gads': 'ID=fe861d45f5db215a:T=1698864883:RT=1698937120:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg',
        '__gpi': 'UID=00000cb0f49e709a:T=1698864883:RT=1698937120:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA',
        '_ga_6YZLS7YDS7': 'GS1.1.1698936664.6.1.1698937188.59.0.0',
        '__tld__': 'null',
        '_gat': '1',
        '_ga': 'GA1.2.1691651900.1698864884',
        '_gat_UA-20095530-1': '1',
    }

    headers = {
        'authority': 'krisha.kz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'krishauid=27a90cf7866809318956bbaf46bf1bee0566a1c3; _gid=GA1.2.1622783382.1698864884; ssaid=1eb3cdf0-78e8-11ee-a9d4-ad9ab41bfaa8; _ym_uid=1698864885305000808; _ym_d=1698864885; _gcl_au=1.1.628254214.1698864887; _tt_enable_cookie=1; _ttp=z6CqOsq7az43qG0d1Q6z7yqkUep; _fbp=fb.1.1698864889126.1219622591; __gsas=ID=387fb42e7e2c73ba:T=1698864889:RT=1698864889:S=ALNI_MZYaWC_3MrfrarwirA-hbO66maZ9A; tutorial=%7B%22add-note%22%3A%22viewed%22%2C%22advPage%22%3A%22viewed%22%2C%22layoutPageContacts%22%3A%22viewed%22%7D; hist_region=2; krssid=1hmnc1jtddkmadcg645sodsvo8; _ym_visorc=b; kr_cdn_host=//alakt-kz.kcdn.online; _ym_isad=2; __gads=ID=fe861d45f5db215a:T=1698864883:RT=1698937120:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg; __gpi=UID=00000cb0f49e709a:T=1698864883:RT=1698937120:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA; _ga_6YZLS7YDS7=GS1.1.1698936664.6.1.1698937188.59.0.0; __tld__=null; _gat=1; _ga=GA1.2.1691651900.1698864884; _gat_UA-20095530-1=1',
        'referer': 'https://krisha.kz/a/show/667124453',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'alias': 'almaty/koktobe-siti',
    }

    response = requests.get('https://krisha.kz/complex/ajaxPhones', params=params, cookies=cookies, headers=headers)

    print(response.json())

def get_data(session, pages):
    result_list = []

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    # browser.maximize_window()


    for i in range(1, pages + 1)[:1]:
        url = f"https://krisha.kz/prodazha/kvartiry/?das[house.year][to]=2023&das[price][from]=90000000&das[who]=" \
              f"1&page={i}"

        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find_all('div', class_='a-card__descr')
        except Exception as ex:
            data = []
        for item in data:
            try:
                url = f"https://krisha.kz{item.find('a', class_='a-card__title').get('href')}"
            except Exception as ex:
                url = None

            try:
                city = item.find_next('div', class_='a-card__stats-item').text.strip()
            except Exception:
                city = None

            try:
                title = ', '.join((item.find('a', class_='a-card__title').text.strip(),
                                   item.find('div', class_='a-card__subtitle').text.strip()))
            except Exception:
                title = None
            try:
                price = item.find('div', class_='a-card__price').text.strip()
            except Exception:
                price = None
            try:
                # browser.implicitly_wait(5)
                time.sleep(15)
                browser.get(url=url)
            except Exception as ex:
                print(ex)
            try:

                # button = WebDriverWait(browser, 5).until(
                #     EC.element_to_be_clickable((By.CLASS_NAME, 'show-phones')))
                button = browser.find_element((By.CLASS_NAME, 'show-phones'))
                button.click()
            except Exception as ex:
                print(ex)

            print(f'url-{url}|||city-{city}|||title-{title}|||price-{price}|||phones-{phones}')

            # result_list.append(
            #     (
            #         url,
            #         city,
            #         description,
            #         price,
            #         phones
            #     )
            # )

        print(f'Processed: {i} pages')
    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    # with requests.Session() as session:
    #     html = get_html(url=url, headers=headers, session=session)
    #     pages = get_pages(html)
    #     print(f'Total: {pages} pages')
    #     data = get_data(session=session, pages=pages)
    get_phone()
    # execution_time = datetime.now() - start_time
    # print('Сбор данных завершен!')
    # print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
