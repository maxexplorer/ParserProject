import requests
import os
from datetime import datetime
import json
from pandas import DataFrame, ExcelWriter

headers = {
    'authority': 'api-open-nostroy.anonamis.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://reestr.nostroy.ru',
    'referer': 'https://reestr.nostroy.ru/',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}

start_time = datetime.now()

exceptions_list = []


def get_id(headers, region):
    json_data = {
        'filters': {'member_status': 2, 'region_number': region},
        'page': 1,
        'pageCount': '100',
        'sortBy': {},
    }

    session = requests.Session()
    response = session.post('https://api-open-nostroy.anonamis.ru/api/sro/all/member/list', headers=headers,
                            json=json_data)

    data = response.json()

    page_count = int(data['data']['countPages'])
    print(page_count)

    id_list = []

    with requests.Session() as session:
        for page in range(1, page_count + 1):
            json_data = {
                'filters': {'member_status': 2, 'region_number': region},
                'page': page,
                'pageCount': '100',
                'sortBy': {},
            }

            try:
                response = session.post('https://api-open-nostroy.anonamis.ru/api/sro/all/member/list', headers=headers,
                                        json=json_data)

                data = response.json()

            except Exception as ex:
                print(ex)
                continue

            try:
                for item in data['data']['data']:
                    id_list.append(item['id'])
            except Exception as ex:
                print(ex)
                continue

            print(page)

        with open('data/id_list.txt', 'a', encoding='utf-8') as file:
            print(*id_list, file=file, sep='\n')


def get_data(file_path, headers):
    with open(file_path, 'r', encoding='utf-8') as file:
        id_list = [line.strip() for line in file.readlines()]

    json_data = {}

    result_list = []

    with requests.Session() as session:
        for i, item in enumerate(id_list[10000:20000], 1):
            try:
                response = session.post(f"https://api-open-nostroy.anonamis.ru/api/member/{item}/info",
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
                city = data['data']['region_number']['title'].strip()
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

            # print(f'{i}/{len(id_list)}')
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

    with ExcelWriter('data/data.xlsx', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name='data3')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    # region = int(input("Введите регион: 77 - Москва, 52 - Московская область"))
    # get_id(headers=headers, region=region)
    data = get_data(file_path='data/id_list.txt', headers=headers)
    save_json(data)
    save_excel(data)
    if len(exceptions_list) > 0:
        with open('data/exceptions_list.txt', 'a', encoding='utf-8') as file:
            print(*exceptions_list, file=file, sep='\n')
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
