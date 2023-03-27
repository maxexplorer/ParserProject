import requests
import asyncio
import aiohttp
import os
from datetime import datetime
import json
from pandas import DataFrame, ExcelWriter
import openpyxl

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

result_list = []


async def get_data(session, i, item):
    json_data = {}

    try:
        async with session.post(f"https://api-open-nostroy.anonamis.ru/api/member/{item}/info",
                                headers=headers, json=json_data) as response:
            data = await response.json()
    except Exception:
        pass

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
        city = data['data']['locality'].strip()
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


async def gather_data():
    with open('data/id_list.txt', 'r', encoding='utf-8') as file:
        id_list = [line.strip() for line in file.readlines()]
    async with aiohttp.ClientSession() as session:
        tasks = []

        for i, item in enumerate(id_list[:100], 1):
            task = asyncio.create_task(get_data(session, i, item))
            tasks.append(task)

        await asyncio.gather(*tasks)


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    # writer = ExcelWriter('data/data.xlsx', mode='w')
    # dataframe.to_excel(writer, sheet_name='data')
    # writer.save()
    # is equivalent to

    with ExcelWriter('data/data_asyncio.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


async def main():
    await gather_data()
    save_excel(result_list)

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
