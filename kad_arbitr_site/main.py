import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import pandas as pd
from pandas import DataFrame, ExcelWriter
import xlsxwriter


def get_data(data_list):
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
        '_ym_isad': '2',
        'rcid': 'fb3c3667-e7ec-41a8-9243-0b501e80bff3',
        'tmr_detect': '0%7C1686249439775',
        'wasm': 'd98631d33fda423afaf059f36f1d8dbe',
        '_gat': '1',
    }

    headers = {
        'authority': 'kad.arbitr.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        # 'cookie': '__ddg1_=MFMXvDe9vnfJ6yyzwrhA; ASP.NET_SessionId=2tbhmmracsoxnyzj0hv3nqij; CUID=0e4e384b-57f0-429d-ab85-d3725a50463b:lXvk7RX5VuP9bMqQEgNZaQ==; _ga=GA1.2.1343078113.1686207225; _gid=GA1.2.6857850.1686207225; _ym_uid=1686207227142264491; _ym_d=1686207227; pr_fp=b8b6c4acd80151855d63363388cf302ae16a2b028cc87c7de3b2f8c6239c4650; tmr_lvid=f106a92d04e109ac6cd53242d170122c; tmr_lvidTS=1686207226755; _ym_isad=2; rcid=fb3c3667-e7ec-41a8-9243-0b501e80bff3; tmr_detect=0%7C1686249439775; wasm=d98631d33fda423afaf059f36f1d8dbe; _gat=1',
        'origin': 'https://kad.arbitr.ru',
        'referer': 'https://kad.arbitr.ru/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
        'x-date-format': 'iso',
        'x-requested-with': 'XMLHttpRequest',
    }

    result_list = []

    with requests.Session() as session:
        for i, tin, full_name, address, date, num_case in data_list[1:2]:
            if tin.strip():
                name = tin
            else:
                name = full_name.strip()
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
            try:
                response = session.post('https://kad.arbitr.ru/Kad/SearchInstances', cookies=cookies, headers=headers,
                                        json=json_data)
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as ex:
                print(ex)
                continue

            try:
                date = soup.find('span', class_='js-rollover b-newRollover').text.strip()
            except Exception:
                continue
            try:
                num_case = soup.find('a', class_='num_case').text.strip()
            except Exception:
                continue

            result_list.append(
                {
                    'ИНН': tin,
                    'ФИО': full_name,
                    'Адрес собственника': address,
                    'Дата': date,
                    '№ дела': num_case
                }
            )
    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/output_data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    with open('data/input_data.csv', 'r', encoding='cp1251') as file:
        reader = csv.reader(file, delimiter=';')
        data_list = list(reader)
    result_list = get_data(data_list=data_list)
    save_excel(result_list)


if __name__ == '__main__':
    main()
