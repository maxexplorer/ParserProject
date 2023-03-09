import re

import requests
from bs4 import BeautifulSoup
import os
import json
from fake_useragent import UserAgent

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}

url = "https://uzorg.info/companies"


def get_html(url, headers):
    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

    # if not os.path.exists('data'):
    #     os.mkdir('data')
    #
    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)

    html = response.text
    return html


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='col text-center').text.strip().split()[-2])
    except Exception:
        pages = None
    return pages


def get_data():
    cards = []
    # with requests.Session() as session:
    #     for page in range(1, pages + 1):
    #         print(f'Парсинг страницы: {page}')
    #         url = f"https://uzorg.info/companies-page-{page}"
    #         response = session.get(url=url, headers=headers)
    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all(class_='list-group-item')
    for item in items:
        title = item.find('h5', class_='mb-1').text.strip().replace('"', '')
        # tin = int(re.compile(r'\d{8}').search(item.find('p', class_='mb-1').text.strip()).group())
        # is equivalent to
        tin = int(re.search(r'\d{8}', item.find('p', class_='mb-1').text.strip()).group())
        string = item.find('p', class_='mb-1').text.strip()
        index = string.find(str(tin)) + 9
        activity = string[index:]
        date = item.find('small', class_='text-muted').text.strip()
        director = ' '.join(item.find(text=re.compile('Руководитель')).text.split()[-3:])
        address = ' '.join(item.find(text=re.compile('Адрес')).text.split()[2:])
        status = item.find('font').text.strip()

        cards.append(
            {
                'Название': title,
                'ИНН': tin,
                'Деятельность': activity,
                'Дата основания': date,
                'Руководитель': director,
                'Адрес': address,
                'Статус': status
            }
        )
    return cards


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print('Данные сохранены в файл "data.json"')


def main():
    # html = get_html(url=url, headers=headers)
    # pages = get_pages(html)
    # print(f'Количество страниц: {pages}')
    # pages = int(input('Введите количество страниц: '))
    data = get_data()
    save_json(data)


if __name__ == '__main__':
    main()
