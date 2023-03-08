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


def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all(class_='list-group-item')
    for card in cards:
        title = card.find('h5', class_='mb-1').text.strip()
        tin = int(re.search(r'\d{8}', card.find('p', class_='mb-1').text.strip()).group())
        # activity = re.search(r'.*', card.find('p', class_='mb-1').text.strip())
        string = card.find('p', class_='mb-1').text.strip()
        index = string.find(str(tin)) + 9
        string = string[index:]

        print(f"{title} ||| {tin} ||| {(string)}")

def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print('Данные сохранены в файл "data.json"')

def main():
    # html = get_html(url=url, headers=headers)
    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    # pages = get_pages(html)
    get_data(html)
    # print(f'Количество страниц: {pages}')
    # cards = []
    # pages = int(input('Введите количество страниц: '))
    # for page in range(1, pages + 1):
    #     print(f'Парсинг страницы: {page}')
    #     url = f"https://uzorg.info/companies-page-{page}"
    #     html = get_html(url=url, headers=headers)
    #     cards.extend(get_data(html))


if __name__ == '__main__':
    main()
