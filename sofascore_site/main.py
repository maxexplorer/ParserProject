import json

import requests
from datetime import datetime
import os
import csv


start_time = datetime.now()

url = "https://www.sofascore.com/ru/tennis/rankings/atp"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


# Получаем html разметку страницы
def get_json(url: str, headers: dict, session: requests.sessions.Session) -> str:
    """
    :param url: str
    :param headers: dict
    :param session: requests.sessions.Session
    :return: str
    """

    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(response.status_code)

        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_players_rankings():

    headers = {
        'authority': 'api.sofascore.com',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'if-none-match': 'W/"317ae73a0a"',
        'origin': 'https://www.sofascore.com',
        'referer': 'https://www.sofascore.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
    }

    with requests.Session() as session:
        response = session.get('https://api.sofascore.com/api/v1/rankings/type/5', headers=headers)

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/players_rankings.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def save_csv(data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/result_data_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('vendor: Производитель',
             'folder: Категория',
             'article: Артикул',
             'name: Название',
             'price: Цена',
             'image: Иллюстрация',
             'body: Описание',
             'amount : Количество'
             )
        )

    with open(f'data/results_data_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    get_players_rankings()

if __name__ == '__main__':
    main()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')
