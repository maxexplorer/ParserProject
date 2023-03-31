import re
import requests
from bs4 import BeautifulSoup
import os
import json
from fake_useragent import UserAgent
from datetime import datetime

start_time = datetime.now()

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}
name = 'Иванов'

url = f"https://mos-sud.ru/search?participant={name}"

def get_data():
    response = requests.get(url=url, headers=headers, verify=False)

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)


def main():
    get_data()
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')

if __name__ == '__main__':
    main()
