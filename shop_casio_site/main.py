import csv
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

url = "https://shop.casio.ru/catalog/filter/gender-is-male/apply/"
useragent = UserAgent()


def get_all_pages(url):
    headers = {
        'user-agent': useragent.random
    }

    # req = requests.get(url=url, headers=headers)
    # print(req.headers['Content-Type'])
    #
    # if not os.path.exists('data'):
    #     os.mkdir('data')
    #
    # with open('data/page_1.html', 'w', encoding='utf-8') as file:
    #     file.write(req.text)

    with open('data/page_1.html', 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    pages_count = int(soup.find('div', class_='bx-pagination-container').find_all('a')[-2].text)
    print(pages_count)
    for i in range(1, pages_count + 1):
        url = f"https://shop.casio.ru/catalog/filter/gender-is-male/apply/?PAGEN_1={i}"

        req = requests.get(url=url, headers=headers)

        with open(f'data/page_{i}.html', 'w', encoding='utf-8') as file:
            file.write(req.text)

        time.sleep(2)

    return pages_count + 1


def collect_data(pages_count):
    cur_date = datetime.now().strftime("%d-%m-%Y")

    data = []

    with open(f'data/data_{cur_date}.csv', 'w', encoding='cp1251') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'Артикул',
                'Ссылка'
            )
        )

    for page in range(1, pages_count):
        with open(f'data/page_{page}.html', 'r', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        items_cards = soup.find_all('a', class_="product-item__link")

        for item in items_cards:
            product_article = item.find('p', class_="product-item__articul").text.strip()
            product_url = f"https://shop.casio.ru{item.get('href')}"

            data.append({
                'product_article': product_article,
                'product_url': product_url
            })

            with open(f'data/data_{cur_date}.csv', 'a', encoding='1251') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        product_article,
                        product_url
                    )
                )

        print(f'Обработана страница {page}')

    with open(f'data/data_{cur_date}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    page_count = get_all_pages(url)
    collect_data(pages_count=page_count)


if __name__ == '__main__':
    main()
