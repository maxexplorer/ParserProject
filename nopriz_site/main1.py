import requests
import os
from datetime import datetime
from config import cookies, headers
import json
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

exceptions_list = []


def get_id(cookies, headers):
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


def get_data(file_path, cookies, headers):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_list = [line.strip() for line in file.readlines()]

    json_data = {}

    result_list = []

    with requests.Session() as session:
        for i, item in enumerate(id_list, 1):
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

            print(i)

    return result_list


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'a', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    # writer = ExcelWriter('data/data.xlsx', mode='w')
    # dataframe.to_excel(writer, sheet_name='data')
    # writer.save()
    # is equivalent to

    with ExcelWriter('data/data1.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    # get_id(cookies=cookies, headers=headers)
    data = get_data(file_path='data/exceptions_list.txt', cookies=cookies, headers=headers)
    save_json(data)
    save_excel(data)
    if len(exceptions_list) > 0:
        with open('data/exceptions_list.txt', 'w', encoding='utf-8') as file:
            print(*exceptions_list, file=file, sep='\n')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
