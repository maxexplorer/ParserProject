import os
import time
from datetime import datetime
import csv
from random import randrange

import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent

start_time = datetime.now()
cur_date = datetime.now().strftime('%d-%m-%Y')

useragent = UserAgent()

def get_data(data_list):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_date}.csv', 'w', encoding='cp1251', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                'ИНН',
                'ИНН1',
                'ФИО',
                'Адрес',
                'Дата',
                '№ дела'
            )
        )

    cookies = {
        '__ddg1_': 'hJ2gus2Uk92lVa8Ah0I1',
        'ASP.NET_SessionId': 'd0afrxkozgstybxowcc305pw',
        'CUID': '612d9663-2b2e-4e58-b738-e4d1375b6f03:xQO0mrvJC121L36Lxa2Eew==',
        '_ga': 'GA1.2.514976819.1686401335',
        'pr_fp': 'b8b6c4acd80151855d63363388cf302ae16a2b028cc87c7de3b2f8c6239c4650',
        'tmr_lvid': '9e02cdea92d0e9183c217e306b5a8a19',
        'tmr_lvidTS': '1686401337221',
        '_ym_uid': '1686401338199628375',
        '_ym_d': '1686401338',
        'rcid': '05df19e5-f8a9-499b-909d-dbc2f2d16af4',
        'Notification_All': 'c39d51b8a1ec4d009f00910dc65bf624_1688317200000_shown',
        '__ddgid_': 'gEZsaD1SqQ2cWrLj',
        '__ddg2_': 'ieddKCUsnIp2Eavn',
        '_gid': 'GA1.2.1566152723.1688470817',
        '_ym_isad': '2',
        'wasm': '6bd4cbe0827915f47734a95a102c4cd3',
        '_gat': '1',
        '_gat_FrontEndTracker': '1',
        '_dc_gtm_UA-157906562-1': '1',
        '_ga_Q2V7P901XE': 'GS1.2.1688472858.3.0.1688472858.0.0.0',
        'tmr_detect': '0%7C1688472860717',
    }

    headers = {
        'authority': 'kad.arbitr.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        # 'cookie': '__ddg1_=hJ2gus2Uk92lVa8Ah0I1; ASP.NET_SessionId=d0afrxkozgstybxowcc305pw; CUID=612d9663-2b2e-4e58-b738-e4d1375b6f03:xQO0mrvJC121L36Lxa2Eew==; _ga=GA1.2.514976819.1686401335; pr_fp=b8b6c4acd80151855d63363388cf302ae16a2b028cc87c7de3b2f8c6239c4650; tmr_lvid=9e02cdea92d0e9183c217e306b5a8a19; tmr_lvidTS=1686401337221; _ym_uid=1686401338199628375; _ym_d=1686401338; rcid=05df19e5-f8a9-499b-909d-dbc2f2d16af4; Notification_All=c39d51b8a1ec4d009f00910dc65bf624_1688317200000_shown; __ddgid_=gEZsaD1SqQ2cWrLj; __ddg2_=ieddKCUsnIp2Eavn; _gid=GA1.2.1566152723.1688470817; _ym_isad=2; wasm=6bd4cbe0827915f47734a95a102c4cd3; _gat=1; _gat_FrontEndTracker=1; _dc_gtm_UA-157906562-1=1; _ga_Q2V7P901XE=GS1.2.1688472858.3.0.1688472858.0.0.0; tmr_detect=0%7C1688472860717',
        'origin': 'https://kad.arbitr.ru',
        'referer': 'https://kad.arbitr.ru/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': useragent.random,
        'x-date-format': 'iso',
        'x-requested-with': 'XMLHttpRequest',
    }
    with requests.Session() as session:
        if not os.path.exists('data'):
            os.mkdir('data')

        for i, tin, full_name, address in data_list[373:500]:
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

            time.sleep(randrange(3, 5))

            try:
                response = requests.post('https://kad.arbitr.ru/Kad/SearchInstances', cookies=cookies, headers=headers,
                                         json=json_data, timeout=30)

                if response.status_code == 451:
                    print(f'{i}: {response}')
                    break
                soup = BeautifulSoup(response.text, 'lxml')
            except Exception as ex:
                print(ex)
                continue

            items = soup.find_all('tr')
            for item in items:
                item: BeautifulSoup
                try:
                    date = item.find(class_='b-icon').find_next().find_next().text.strip()
                except Exception:
                    date = None
                try:
                    num_case = item.find('a', class_='num_case').text.strip()
                except Exception:
                    num_case = None
                try:
                    tin1 = item.find(string=re.compile('ИНН')).text.replace('ИНН:', '').strip()
                except Exception:
                    tin1 = None

                with open(f'data/data_{cur_date}.csv', 'a', encoding='cp1251', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(
                        (
                            tin,
                            tin1,
                            full_name,
                            address,
                            date,
                            num_case
                        )
                    )

            print(f'Выполнено: {i}/{len(data_list)}')


def main():
    with open('data/input_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        data_list = list(reader)
    print(f'Всего: {len(data_list)}')
    get_data(data_list=data_list)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
