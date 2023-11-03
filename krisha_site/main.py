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


def get_phones_selenium(url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()

    try:
        browser.implicitly_wait(5)
        browser.get(url=url)

        browser.switch_to.alert.accept()

    except Exception as ex:
        print(ex)
    try:
        element = browser.find_element(By.CSS_SELECTOR, 'button.show-phones')
        element.click()
    except Exception as ex:
        print(ex)
    try:
        button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'show-phones')))
        button.click()
    except Exception as ex:
        print(ex)


def get_phones_api():
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
        '_ym_isad': '2',
        '_ym_visorc': 'b',
        '__gads': 'ID=fe861d45f5db215a:T=1698864883:RT=1698945467:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg',
        '__gpi': 'UID=00000cb0f49e709a:T=1698864883:RT=1698945467:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA',
        'kr_cdn_host': '//alakt-kz.kcdn.online',
        '_ga_6YZLS7YDS7': 'GS1.1.1698945469.8.1.1698945541.60.0.0',
        '_gat': '1',
        '_ga': 'GA1.2.1691651900.1698864884',
        '_gat_UA-20095530-1': '1',
        '__tld__': 'null',
    }

    headers = {
        'authority': 'krisha.kz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'krishauid=27a90cf7866809318956bbaf46bf1bee0566a1c3; _gid=GA1.2.1622783382.1698864884; ssaid=1eb3cdf0-78e8-11ee-a9d4-ad9ab41bfaa8; _ym_uid=1698864885305000808; _ym_d=1698864885; _gcl_au=1.1.628254214.1698864887; _tt_enable_cookie=1; _ttp=z6CqOsq7az43qG0d1Q6z7yqkUep; _fbp=fb.1.1698864889126.1219622591; __gsas=ID=387fb42e7e2c73ba:T=1698864889:RT=1698864889:S=ALNI_MZYaWC_3MrfrarwirA-hbO66maZ9A; tutorial=%7B%22add-note%22%3A%22viewed%22%2C%22advPage%22%3A%22viewed%22%2C%22layoutPageContacts%22%3A%22viewed%22%7D; hist_region=2; krssid=1hmnc1jtddkmadcg645sodsvo8; _ym_isad=2; _ym_visorc=b; __gads=ID=fe861d45f5db215a:T=1698864883:RT=1698945467:S=ALNI_Ma1y5TB3FKovqAIamaVsuTfA8UUHg; __gpi=UID=00000cb0f49e709a:T=1698864883:RT=1698945467:S=ALNI_MZgBXydABa2ts2fS-GFzf3L00abkA; kr_cdn_host=//alakt-kz.kcdn.online; _ga_6YZLS7YDS7=GS1.1.1698945469.8.1.1698945541.60.0.0; _gat=1; _ga=GA1.2.1691651900.1698864884; _gat_UA-20095530-1=1; __tld__=null',
        'referer': 'https://krisha.kz/a/show/688593604',
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
        'id': '688593604',
        'gRecaptchaResponse': '03AFcWeA63iHyKgVR6nATnBt5MZ2R5m5LUjFXfaGUXJ8CIa_L39thrNlJSL0a9uSPiEQGMDiGR-4QvavpMBpYR1wTA2FxNnoOEAGPYW_CmEWSTfxmtO-570dtci2H50XLr9b_6MFNHK4gzdMfEwYpB-5FX1xrBepNtIZ1-LMifvExXZj8tJaE-hIMQXygoo1wLihbLe7z2pA9b6Id_21of7K3ujGbphULiA0LcszNmdL2o-UHp-V5G_h8_LCcEL3bjokwCl88KUcRz7mDxDL6rdzSgWPYbhJWEzl9WwLJr0n3bDFUQstI22TWWyxwoabzIVvsc6F93SSoedMIus8upkOB5liPKPthf8qiyHfm3MX5kzMoFssulrpcP0vcgYw-ux8p2ZSpVbMk-GMiBKGPo9PoTElnv_Ipa5MJLV-zZl5WIXxjModxx1nEcprDZsWjxCO-tq2D4D-5Q988N_KlIftXGyo8LNB8lthDEz-KUpnNDXZWUGuQYyxDBjIVfBhRhZWFsKDiEWlvFrTkwf3XwT7OJckYqc3FZpUEGRuV7lFyKZ92iX0Ecscg',
    }

    response = requests.get('https://krisha.kz/a/ajaxPhones', params=params, cookies=cookies, headers=headers)

    print(response.json())


def get_data(session, pages):
    result_list = []

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

            print(f'url-{url}|||city-{city}|||title-{title}|||price-{price}')

            result_list.append(
                (
                    url,
                    city,
                    title,
                    price,
                )
            )

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
    get_phones_selenium(url="https://krisha.kz/a/show/677557844")
    # execution_time = datetime.now() - start_time
    # print('Сбор данных завершен!')
    # print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
