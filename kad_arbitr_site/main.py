import os
import time
from datetime import datetime
import csv
from random import randrange

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter
import xlsxwriter

start_time = datetime.now()


def get_data(data_list):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    cookies = {
        '__ddg1_': 'MFMXvDe9vnfJ6yyzwrhA',
        'ASP.NET_SessionId': '2tbhmmracsoxnyzj0hv3nqij',
        'CUID': '0e4e384b-57f0-429d-ab85-d3725a50463b:lXvk7RX5VuP9bMqQEgNZaQ==',
        '_ga': 'GA1.2.1343078113.1686207225',
        '_gid': 'GA1.2.6857850.1686207225',
        '_ym_uid': '1686207227142264491',
        '_ym_d': '1686207227',
        'pr_fp': 'b8b6c4acd80151855d63363388cf302ae16a2b028cc87c7de3b2f8c6239c4650',
        'tmr_lvid': 'f106a92d04e109ac6cd53242d170122c',
        'tmr_lvidTS': '1686207226755',
        'rcid': 'fb3c3667-e7ec-41a8-9243-0b501e80bff3',
        'KadLVCards': '%d0%9051-15519%2f2022~%d0%9045-35689%2f2022~%d0%9035-2799%2f2023',
        'Notification_All': '30df2e13dfef4d2c8ba032b052f13d53_1686603540000_shown',
        '_gat': '1',
        '_gat_FrontEndTracker': '1',
        '_dc_gtm_UA-157906562-1': '1',
        '_ym_isad': '2',
        'tmr_detect': '0%7C1686394780675',
        'wasm': 'a541649da9e17ec183c3a6fa34a4c8a5',
    }

    headers = {
        'authority': 'kad.arbitr.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        # 'cookie': '__ddg1_=MFMXvDe9vnfJ6yyzwrhA; ASP.NET_SessionId=2tbhmmracsoxnyzj0hv3nqij; CUID=0e4e384b-57f0-429d-ab85-d3725a50463b:lXvk7RX5VuP9bMqQEgNZaQ==; _ga=GA1.2.1343078113.1686207225; _gid=GA1.2.6857850.1686207225; _ym_uid=1686207227142264491; _ym_d=1686207227; pr_fp=b8b6c4acd80151855d63363388cf302ae16a2b028cc87c7de3b2f8c6239c4650; tmr_lvid=f106a92d04e109ac6cd53242d170122c; tmr_lvidTS=1686207226755; rcid=fb3c3667-e7ec-41a8-9243-0b501e80bff3; KadLVCards=%d0%9051-15519%2f2022~%d0%9045-35689%2f2022~%d0%9035-2799%2f2023; Notification_All=30df2e13dfef4d2c8ba032b052f13d53_1686603540000_shown; _gat=1; _gat_FrontEndTracker=1; _dc_gtm_UA-157906562-1=1; _ym_isad=2; tmr_detect=0%7C1686394780675; wasm=a541649da9e17ec183c3a6fa34a4c8a5',
        'origin': 'https://kad.arbitr.ru',
        'referer': 'https://kad.arbitr.ru/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) '
                      'Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
        'x-date-format': 'iso',
        'x-requested-with': 'XMLHttpRequest',
    }

    with requests.Session() as session:
        for i, tin, full_name, address, _, _ in data_list[1:]:
            tin = tin.strip()
            full_name = full_name.strip()
            if tin:
                name = tin
            else:
                name = full_name
            json_data = {
                'Page': 1,
                'Count': 25,
                'CaseType': 'B',
                'Courts': [],
                'DateFrom': None,
                'DateTo': None,
                'Sides': [
                    {
                        'Name': f'{name}',
                        'Type': -1,
                        'ExactMatch': False,
                    },
                ],
                'Judges': [],
                'CaseNumbers': [],
                'WithVKSInstances': False,
            }

            session.headers.update(headers)
            session.cookies.update(cookies)

            time.sleep(randrange(3, 5))

            try:
                response = session.post('https://kad.arbitr.ru/Kad/SearchInstances', cookies=cookies, headers=headers,
                                        json=json_data, timeout=30)

                if response.status_code == 451:
                    print(f'{i}: {response}')
                    break
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as ex:
                print(ex)
                continue
            print(f'Обрабатывается: {i}/{len(data_list)}')
            try:
                date = soup.find('span', class_='js-rollover b-newRollover').text.strip()
            except Exception:
                date = None
            try:
                num_case = soup.find('a', class_='num_case').text.strip()
            except Exception:
                num_case = None
            if date is None and num_case is None:
                print(f'{full_name}: нет данных')
                continue

            with open(f'data/data_{cur_date}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        tin,
                        full_name,
                        address,
                        date,
                        num_case
                    )
                )

    print(f'Данные сохранены в файл "data.csv"')


def main():
    with open('data/input_data.csv', 'r', encoding='cp1251') as file:
        reader = csv.reader(file, delimiter=';')
        data_list = list(reader)
    print(f'Всего: {len(data_list)}')
    get_data(data_list=data_list)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')





if __name__ == '__main__':
    main()
