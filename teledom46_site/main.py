import requests
import os
from datetime import datetime
import json


url = "http://teledom46.ru/"
# url = "https://pcshop33.ru/"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


start_time = datetime.now()

def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return response, html
    except Exception as ex:
        print(ex)


def save_json(data):
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_time}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')




def main():
    session = requests.Session()

    response, html = get_html(url=url, headers=headers, session=session)

    print(response.status_code)
    print(html)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
