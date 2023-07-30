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
        '__ddg1_': 'jw0uUdVEBaSxdSkuwZFZ',
        'ASP.NET_SessionId': 'cjfutevowfqxpac4hjhlfbjq',
        'CUID': '2911935a-8bdf-41a8-80b4-4cab66cfb8bd:/PBC4cszH/0sn9+kiSvCYA==',
        '_ga': 'GA1.2.1950699312.1690206769',
        'tmr_lvid': '2617d02c6757bc3c4584daab844ac08d',
        'tmr_lvidTS': '1690206770102',
        '_ym_uid': '1690206770760299697',
        '_ym_d': '1690206770',
        'rcid': '6d5e016c-c826-4142-955a-af1f8d8f68ac',
        'pr_fp': '5aba577ffd016e32a6c7b5f49857d9a089b6fceb34a890d01ac55a8686bd0698',
        '__ddgid_': 'KrQiXi8xINhL7jQo',
        '__ddg2_': 'Z3KrldeV1uLJ8GWw',
        '_gid': 'GA1.2.1178332736.1690705639',
        '_gat': '1',
        '_gat_FrontEndTracker': '1',
        '_dc_gtm_UA-157906562-1': '1',
        '_ym_isad': '2',
        'wasm': '6d1cd3b38985b699538e0bb208796d33',
        '_ga_9582CL89Y6': 'GS1.2.1690705639.8.1.1690705654.45.0.0',
        '_ga_Q2V7P901XE': 'GS1.2.1690705639.8.1.1690705654.0.0.0',
        '_ga_EYS41HMRV3': 'GS1.2.1690705639.8.1.1690705654.45.0.0',
        'tmr_detect': '0%7C1690705656953',
    }

    headers = {
        'authority': 'kad.arbitr.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        # 'cookie': '__ddg1_=jw0uUdVEBaSxdSkuwZFZ; ASP.NET_SessionId=cjfutevowfqxpac4hjhlfbjq; CUID=2911935a-8bdf-41a8-80b4-4cab66cfb8bd:/PBC4cszH/0sn9+kiSvCYA==; _ga=GA1.2.1950699312.1690206769; tmr_lvid=2617d02c6757bc3c4584daab844ac08d; tmr_lvidTS=1690206770102; _ym_uid=1690206770760299697; _ym_d=1690206770; rcid=6d5e016c-c826-4142-955a-af1f8d8f68ac; pr_fp=5aba577ffd016e32a6c7b5f49857d9a089b6fceb34a890d01ac55a8686bd0698; __ddgid_=KrQiXi8xINhL7jQo; __ddg2_=Z3KrldeV1uLJ8GWw; _gid=GA1.2.1178332736.1690705639; _gat=1; _gat_FrontEndTracker=1; _dc_gtm_UA-157906562-1=1; _ym_isad=2; wasm=6d1cd3b38985b699538e0bb208796d33; _ga_9582CL89Y6=GS1.2.1690705639.8.1.1690705654.45.0.0; _ga_Q2V7P901XE=GS1.2.1690705639.8.1.1690705654.0.0.0; _ga_EYS41HMRV3=GS1.2.1690705639.8.1.1690705654.45.0.0; tmr_detect=0%7C1690705656953',
        'origin': 'https://kad.arbitr.ru',
        'referer': 'https://kad.arbitr.ru/',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
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

        for i, tin, full_name, address in data_list[2884:3500]:
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

            # time.sleep(randrange(5, 10))

            try:
                response = session.post('https://kad.arbitr.ru/Kad/SearchInstances', cookies=cookies, headers=headers,
                                         json=json_data, timeout=30)

                if response.status_code == 451 or response.status_code == 429:
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
