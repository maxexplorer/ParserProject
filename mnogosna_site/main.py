import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
from config import cookies, headers

# cookies = {'your': 'cookies'}
# headers = {'your': 'headers'}
size_id = '13573'  # "80x190"


def get_pages():
    useragent = UserAgent()

    headers = {
        'accept': '*/*',
        'user-agent': useragent.random
    }

    url = "https://mnogosna.ru/tipy-matrasov/matrasy/"

    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

    soup = BeautifulSoup(response.text, 'lxml')

    pages = int(soup.find_all('a', class_='pagination__item')[-1].text.strip())

    return pages


def get_data(pages):
    cards = []

    data = {
        'act': 'getListSizes',
        'size_id': size_id,
        'list': '[1373,1438691,329,1096476,9622,1096685,11290,330,5189,11294,1309,9624,387,327,1438686,5187,11293,1438764,9620,1096670,855,11295,5186,13191,1096689,11298,349,5184,6603]',
    }

    with requests.Session() as session:
        for page in range(1, pages + 1):
            print(f'Парсинг страницы: {page}')
            response = session.post('https://mnogosna.ru/local/ajax/product.php', cookies=cookies, headers=headers, data=data)

    with open('data/data1.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def main():
    pages = get_pages()
    print(f'Количество страниц: {pages}')
    pages = int(input('Введите количество страниц: '))
    data = get_data(pages)


if __name__ == '__main__':
    main()
