import requests
import os
from datetime import datetime
import json
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

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

exceptions_list = []


def get_id(file_path, cookies, headers):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_list = [line.strip() for line in file.readlines()]

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
    print(f'Для сбора новых id будет обработано {page_count} страниц!')

    new_id_list = []

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
                    if item['member_status']['code'] == '1' or str(item['id']) in id_list:
                        continue
                    new_id_list.append(str(item['id']).strip())
            except Exception as ex:
                print(ex)
                continue
            print(f'{page}/{page_count}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/id_list.txt', 'a', encoding='utf-8') as file:
        print(*new_id_list, file=file, sep='\n')

    return new_id_list


def get_data(new_id_list, cookies, headers):
    json_data = {}

    result_list = []

    with requests.Session() as session:
        for i, item in enumerate(new_id_list, 1):
            try:
                response = session.post(f"https://reestr.nopriz.ru/api/member/{item}/info", cookies=cookies,
                                        headers=headers, json=json_data)
                data = response.json()
            except Exception:
                exceptions_list.append(item)
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
                    'Название СРО': title_sro,
                    'Название компании': title_company,
                    'ИНН': inn_number,
                    'Город': city,
                    'ФИО руководителя': director,
                    'Основания прекращения членства': suspension_reason,
                    'Дата исключения': suspension_date
                }
            )

            print(f'Обработано: {i}/{len(new_id_list)}')

    return result_list


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/data.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')


def main():
    new_id_list = get_id(file_path='data/id_list.txt', cookies=cookies, headers=headers)
    len_id_list = len(new_id_list)
    print(f'Новых id {len_id_list}')

    if len_id_list > 0:
        data = get_data(new_id_list, cookies=cookies, headers=headers)
        save_excel(data)

    if len(exceptions_list) > 0:
        with open('data/exceptions_list.txt', 'w', encoding='utf-8') as file:
            print(*exceptions_list, file=file, sep='\n')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()