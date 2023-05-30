import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

city_urls = [
    "https://www.bayut.com/companies/dubai/",
    "https://www.bayut.com/companies/abu-dhabi/",
    "https://www.bayut.com/companies/sharjah/",
    "https://www.bayut.com/companies/ajman/",
    "https://www.bayut.com/companies/ras-al-khaimah/",
    "https://www.bayut.com/companies/umm-al-quwain/",
    "https://www.bayut.com/companies/al-ain/",
    "https://www.bayut.com/companies/fujairah/"
]

start_time = datetime.now()

exceptions_list = []


def get_agency_urls(city_urls):
    useragent = UserAgent()

    headers = {
        'Accept': '*/*',
        'User-agent': useragent.random
    }

    agency_urls = []

    with requests.Session() as session:
        for city_url in city_urls:
            try:
                response = session.get(url=city_url, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as ex:
                print(f'{city_url} - {ex}')
                continue
            try:
                count_pages = int(soup.find('ul', class_='_92c36ba1').find_all('li')[-2].text.strip())
            except Exception:
                count_pages = 0
            for i in range(1, count_pages + 1):
                if i == 1:
                    city_page_url = city_url
                else:
                    city_page_url = f"{city_page_url}page-{i}/"

                try:
                    response = session.get(url=city_page_url, headers=headers)
                    soup = BeautifulSoup(response.text, 'lxml')
                except Exception as ex:
                    print(f'{city_page_url} - {ex}')
                    continue
                try:
                    items = soup.find('ul', class_='_25561c1c').find_all('li')
                except Exception:
                    items = None

                for item in items:
                    try:
                        agency_url = 'https://www.bayut.com/' + item.find('a').get('href')
                    except Exception:
                        agency_url = None

                    agency_urls.append(agency_url)

                    print(f'{city_url}-{agency_url}')

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/agency_urls.txt', 'w', encoding='utf-8') as file:
            print(*agency_urls, file=file, sep='\n')


def get_data(agency_urls):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option('useAutomationExtension', False)

    service = Service(executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })


def main():
    agency_urls = get_agency_urls(city_urls)

    # get_data(agency_urls)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
