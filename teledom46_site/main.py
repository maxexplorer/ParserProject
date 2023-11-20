import time

import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import json
import csv


url = "http://teledom46.ru/"
# url = "https://pcshop33.ru/"

category_urls_list = [
    "http://teledom46.ru/catalog/televizory_audio_video/",
    "http://teledom46.ru/catalog/tekhnika_dlya_kukhni/",
    "http://teledom46.ru/catalog/vstraivaemaya_tekhnika/",
    "http://teledom46.ru/catalog/vytyazhki/",
    "http://teledom46.ru/catalog/tekhnika_dlya_doma/",
    "http://teledom46.ru/catalog/klimaticheskaya_tekhnika/",
    "http://teledom46.ru/catalog/sadovaya-tekhka/"
]

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
        return html
    except Exception as ex:
        print(ex)

def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='module-pagination').find_all('a')[-2].text)
    except Exception:
        pages = 1
    return pages

def get_urls(category_urls_list, headers):
    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    product_urls_list = []

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В {i} категории: {pages} страниц')

            for page in range(1, pages + 1):
                product_url = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('a', class_='thumb shine')
                    for item in data:
                        try:
                            url = "http://teledom46.ru" + item.get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            print(f'Обработано: {i}/{count_urls} категорий')

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*product_urls_list, file=file, sep='\n')

def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(product_urls_list)

    result_list = []
    image_urls_list = []

    with requests.Session() as session:
        for j, product_url in enumerate(product_urls_list, 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                title = soup.find('h2', class_='product_name').text.strip()
            except Exception:
                title = None


def save_json(data):
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_time}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_csv(data):
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_time}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')

def main():
    get_urls(category_urls_list=category_urls_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
