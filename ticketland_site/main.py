import csv

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import datetime
import os
import json
from random import randrange

useragent = UserAgent()
headers = {
    'user-agent': useragent.random
}

start_time = time.time()


def get_urls(url):
    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    pages_count = int(soup.find_all('li', class_='search-pagination__item')[-1].get('data-page-count'))

    url_list = []

    with requests.Session() as session:
        for page in range(1, pages_count + 1):
            url = f"https://www.ticketland.ru/spectacle/page-{page}/"
            response = session.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                data = soup.find_all(class_='card-search card-search--show')
                for item in data:
                    url = 'https://www.ticketland.ru' + item.find('a').get('href')
                    url_list.append(url)
            except Exception as ex:
                print(ex)

            time.sleep(randrange(2, 5))
            print(f'Обработано {page}/{pages_count} страниц')

    with open('data/url_list.txt', 'w', encoding='utf-8') as file:
        print(*url_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    with open('data/result.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название спектакля',
                'Место представления',
                'Дата и время',
                'Цена',
                'Ссылка на изображение',
                'Актеры',
                'Описание'
            )
        )

    urls_count = len(urls_list)
    result_data = []

    with requests.Session() as session:
        for i, url in enumerate(urls_list[:100], 1):
            response = session.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            try:
                title = soup.find('div', class_='show-header__title').find('h1').text.strip()
                place = soup.find('span', class_='show-card__building').text.strip()
                date = [item.text.strip().replace(' ', ' ') for item in soup.find_all('span', class_='show-card__dm')]
                date = [f'{i} {k}' for i, k in zip(date[0::2], date[1::2])]
                time = [item.text.strip() for item in soup.find_all('span', class_='show-card__t')]
                date = [f'{d} {y}' for d, y in zip(date, time)]
                price = soup.find('span', itemprop="price").text.strip().replace(' ', '')
                images = ['https:' + item.get('data-src') for item in
                          soup.find('ul', class_='slides').find_all('img', class_='lazy-show')]
                actors = [actor.text.strip() for actor in soup.find_all('a', class_='person__modal-box')]
                description = ''.join([item.text.strip().replace(' ', '') for item in
                                       soup.find('div', itemprop='description').find_all('p')])

                result_data.append(
                    {
                        'title': title,
                        'place': place,
                        'date': date,
                        'price': price,
                        'images': images,
                        'actors': actors,
                        'description': description
                    }
                )
            except Exception as ex:
                print(ex)

            print(f'Обработано {i}/{urls_count}')

            with open('data/result.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        title,
                        place,
                        date,
                        price,
                        images,
                        actors,
                        description
                    )
                )

    # with open('data/result.json', 'w', encoding='utf-8') as file:
    #     json.dump(result_data, file, indent=4, ensure_ascii=False)


def main():
    # get_urls('https://www.ticketland.ru/spectacle/')
    get_data('data/url_list.txt')
    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    main()
