import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
from config import cookies, headers

# cookies = {'your': 'cookies'}
# headers = {'your': 'headers'}
size_id = '13573'  # "80x190"
# url = "https://mnogosna.ru/po-razmeram/140x200/"


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


def get_data(html):
    cards = []

    # with requests.Session() as session:
    #     for page in range(1, pages + 1):
    #         print(f'Парсинг страницы: {page}')
    #         url = f"https://mnogosna.ru/tipy-matrasov/matrasy/?filter=P_2%3A13499&p={page}"
    #         response = session.get(url=url, headers=headers)
    #         soup = BeautifulSoup(response.text, 'lxml')
    #     with open('data/index.html', 'w', encoding='utf-8') as file:
    #         file.write(response.text)

    soup = BeautifulSoup(html, 'lxml')

    items = soup.find_all('div', class_='col-sm-6 col-md-4 col-lg-3')

    for item in items:
        try:
            title = item.find('div', class_='p-card__name').text.strip()
        except Exception:
            title = None
        try:
            rating = item.find('span', class_='pc-rating__value').text.strip()
        except:
            rating = None
        try:
            status = item.find('div', class_='status status--grid status--available').text.strip()
        except Exception:
            status = None
        try:
            dimensions = item.find('div', class_='select select--xs').text.strip()
        except Exception:
            dimensions = None
        try:
            # price = ''.join(i for i in item.find('div', class_='pc-price__value js-price').text.strip() if i.isdigit())
            # is equivalent to
            price = ''.join(filter(lambda x: x.isdigit(), item.find('div', class_='pc-price__value js-price').text.strip()))
        except Exception:
            price = None
        try:
            old_price = ''.join(filter(lambda x: x.isdigit(), item.find('div', class_='pc-price__old').text.strip()))
        except Exception:
            old_price = None
        try:
            discount = item.find('div', class_='pc-price__discount js-price-discount-percent').text.strip('-')
        except Exception:
            discount = None
        try:
            description = item.find('div', class_='pc-descr').text.strip()
        except Exception:
            description = None
        try:
            url = "https://mnogosna.ru" + item.find('div', class_='p-card__name').find('a').get('href')
        except Exception:
            url = None

        print(f"{title}|||{rating} ||| {status} ||| {dimensions} ||| {price} ||| {old_price} ||| {discount} ||| {description} ||| {url}")




def main():
    # pages = get_pages()
    # print(f'Количество страниц: {pages}')
    # pages = int(input('Введите количество страниц: '))
    # data = get_data(pages)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    get_data(html)


if __name__ == '__main__':
    main()
