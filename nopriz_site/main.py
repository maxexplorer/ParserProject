import requests
import os
from datetime import datetime
import json
import csv

start_time = datetime.now()


def get_id():
    cookies = {
        '_ym_uid': '1679307059271880629',
        '_ym_d': '1679307059',
        '_ym_isad': '2',
        'PHPSESSID': 'UaADUcpxoLi7b46dyIjc6g22dzipOqjj',
        '_ym_visorc': 'w',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        # 'Cookie': '_ym_uid=1679307059271880629; _ym_d=1679307059; _ym_isad=2; PHPSESSID=UaADUcpxoLi7b46dyIjc6g22dzipOqjj; _ym_visorc=w',
        'Origin': 'https://reestr.nopriz.ru',
        'Referer': 'https://reestr.nopriz.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'filters': {},
        'page': 1,
        'pageCount': '1000',
        'sortBy': {},
        'searchString': None,
    }

    session = requests.Session()
    response = session.post('https://reestr.nopriz.ru/api/sro/all/member/list', cookies=cookies, headers=headers,
                            json=json_data)
    data = response.json()
    page_count = int(data['data']['countPages'])
    print(page_count)

    id_list = []

    with requests.Session() as session:
        for page in range(1, page_count + 1):
            json_data = {
                'filters': {},
                'page': page,
                'pageCount': '1000',
                'sortBy': {},
                'searchString': None,
            }

            try:
                response = session.post("https://reestr.nopriz.ru/api/sro/all/member/list", cookies=cookies,
                                        headers=headers,
                                        json=json_data)
                data = response.json()
                for item in data['data']['data']:
                    if item['member_status']['code'] == '1':
                        continue
                    id_list.append(item['id'])
            except Exception as ex:
                print(ex)
                continue
            print(page)
        with open('data/id_list.txt', 'w', encoding='utf-8') as file:
            print(*id_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_list = [line.strip() for line in file.readlines()]

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.csv', 'w', encoding='cp1251', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                'Название СРО',
                'Название компании',
                'ИНН',
                'Город',
                'ФИО руководителя',
                'Основания прекращения членства',
                'Дата исключения'
            )
        )

    cookies = {
        '_ym_uid': '1679307059271880629',
        '_ym_d': '1679307059',
        '_ym_isad': '2',
        'PHPSESSID': 'A96iAA06Iy4yJTJv0DMj85iespuIeF68',
        '_ym_visorc': 'w',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        # 'Cookie': '_ym_uid=1679307059271880629; _ym_d=1679307059; _ym_isad=2; PHPSESSID=A96iAA06Iy4yJTJv0DMj85iespuIeF68; _ym_visorc=w',
        'Origin': 'https://reestr.nopriz.ru',
        'Referer': 'https://reestr.nopriz.ru/member/19483698',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {}

    result_list = []

    with requests.Session() as session:
        for i, item in enumerate(id_list[:10], 1):
            try:
                response = session.post(f"https://reestr.nopriz.ru/api/member/{item}/info", cookies=cookies,
                                        headers=headers, json=json_data)
                data = response.json()
            except Exception as ex:
                print(ex)
                continue

            try:
                title_sro = data['data']['sro']['full_description'].strip()
            except Exception:
                title_sro = None
            try:
                title_company = data['data']['full_description'].strip()
            except Exception:
                title_company = None
            try:
                inn_number = data['data']['inn'].strip()
            except Exception:
                inn_number = None
            try:
                city = ', '.join((data['data']['base_subject']['title'], data['data']['locality']))
            except Exception:
                city = None
            try:
                director = ' '.join(data['data']['director'].strip().split()[-3:])
            except Exception:
                director = None
            try:
                suspension_reason = data['data']['suspension_reason'].strip()
            except Exception:
                suspension_reason = None
            try:
                suspension_date = '.'.join(data['data']['suspension_date'].split('T')[0].split('-')[::-1])
            except Exception:
                suspension_date = None

            result_list.append(
                {
                    'ID': int(item),
                    'Название СРО': title_sro,
                    'Название компании': title_company,
                    'ИНН': int(inn_number),
                    'Город': city,
                    'ФИО руководителя': director,
                    'Основания прекращения членства': suspension_reason,
                    'Дата исключения': suspension_date
                }
            )

            with open('data/data.csv', 'a', encoding='cp1251', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        title_sro,
                        title_company,
                        inn_number,
                        city,
                        director,
                        suspension_reason,
                        suspension_date
                    )
                )
                print(i)

        with open('data/data.json', 'w', encoding='utf-8') as file:
            json.dump(result_list, file, indent=4, ensure_ascii=False)


def update_data():
    pass


def main():
    # get_id()
    get_data(file_path='data/id_list.txt')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()

"""
Нужно название сро 
Название компании 
ИНН 
Регион 
Фио руководителя 
Основания прекращения членства
Дата исключения
"""
