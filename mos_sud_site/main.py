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


def get_urls(headers, name):
    url = f"https://mos-sud.ru/search?participant={name}"

    response = requests.get(url=url, headers=headers, verify=False)

    print(response)

    # soup = BeautifulSoup(response.text, 'lxml')
    #
    # pages = soup.find('div', class_='paginationContainer').find('li', class_='active').text.strip()
    #
    # print(pages)

    # with requests.Session() as session:
    #     for url in range()



def get_data():
    pass

def main():
    # name = input('Введите фамилию или организацию: \n')
    get_urls(headers=headers, name='Иванов')
    # get_data()
    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')

if __name__ == '__main__':
    main()
