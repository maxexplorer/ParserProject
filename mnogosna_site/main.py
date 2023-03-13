import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
import csv
from pandas import DataFrame, ExcelWriter
import openpyxl

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}

size_id_dict = {'80x190': '13573', '90x190': '13499', '180x190': '6682'}
"""
Ширина 70 см: 70 x 186 | 70 x 190 | 70 x 195 | 70 x 200
Ширина 80 см: 80 х 186 | 80 х 190 | 80 х 195 | 80 х 200
Ширина 90 см: 90 х 195 | 90 х 190 | 90 х 200
Ширина 100 см: 100 х 190 | 100 х 195 | 100 х 200
Ширина 110 см: 110 х 190 | 110 х 195 | 110 х 200
Ширина 120 см: 120 х 186 | 120 х 190 | 120 х 195 | 120 х 200
Ширина 130 см: 130 х 190 | 130 х 195 | 130 х 200
Ширина 140 см: 140 х 186 | 140 х 190 | 140 х 195 | 140 х 200
Ширина 150 см: 150 х 190 | 150 х 195 | 150 х 200
Ширина 160 см: 160 х 186 | 160 х 190 | 160 х 195 | 160 х 200 | 160 х 205 | 160 х 210
Ширина 170 см: 170 х 190 | 170 х 195 | 170 х 200
Ширина 180 см: 180 х 190 | 180 х 186 | 180 х 195 | 180 х 200 | 180 х 205 | 180 х 210
Ширина 190 см: 190 х 190 | 190 х 195 | 190 х 200
Ширина 200 см: 200 х 200"""

# url = "https://mnogosna.ru/po-razmeram/140x200/"


def get_pages(url, headers):
    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

    soup = BeautifulSoup(response.text, 'lxml')

    pages = int(soup.find_all('a', class_='pagination__item')[-1].text.strip())

    return pages


def get_data(url, headers, pages):
    cards = []

    with requests.Session() as session:
        for page in range(1, pages + 1):
            print(f'Парсинг страницы: {page}')
            response = session.get(url=url, headers=headers)

            soup = BeautifulSoup(response.text, 'lxml')
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
                    price = ''.join(
                        filter(lambda x: x.isdigit(), item.find('div', class_='pc-price__value js-price').text.strip()))
                except Exception:
                    price = None
                try:
                    old_price = ''.join(
                        filter(lambda x: x.isdigit(), item.find('div', class_='pc-price__old').text.strip()))
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

                cards.append(
                    {
                        'Название': title,
                        'Рейтинг': rating,
                        'Статус': status,
                        'Размеры': dimensions,
                        'Цена': price,
                        'Старая цена': old_price,
                        'Скидка': discount,
                        'Описание': description,
                        'Ссылка': url
                    }
                )
    return cards


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_csv(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ('Название',
            'Рейтинг',
            'Статус',
            'Размеры',
            'Цена',
            'Старая цена',
            'Скидка',
            'Описание',
            'Ссылка')
        )

    with open('data/data.csv', 'a', encoding='utf-8') as file:
        for item in data:
            writer = csv.writer(file)
            writer.writerow(
                (item['Название'],
                 item['Рейтинг'],
                 item['Статус'],
                 item['Размеры'],
                 item['Цена'],
                 item['Старая цена'],
                 item['Скидка'],
                 item['Описание'],
                 item['Ссылка'],)
            )
            # [*(v.values() for v in data)]
    print('Данные сохранены в файл "data.csv"')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    writer = ExcelWriter('data/data.xlsx')
    dataframe.to_excel(writer, 'data')
    writer.save()
    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    cards = []
    for k in size_id_dict.keys():
        print(f'Размеры: {k}')
        url = f"https://mnogosna.ru/tipy-matrasov/matrasy/?filter=P_2%3A{size_id_dict.get(k)}"
        pages = get_pages(url, headers)
        print(f'Количество страниц: {pages}')
        cards.extend(get_data(url, headers, pages))
    save_json(cards)
    save_csv(cards)
    save_excel(cards)

if __name__ == '__main__':
    main()
