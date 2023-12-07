import json

import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://asko-russia.ru/catalog/stiralnye_mashiny/",
    "https://asko-russia.ru/catalog/sushilnye_mashiny/",
    "https://asko-russia.ru/catalog/sushilnye_shkafy/",
    "https://asko-russia.ru/catalog/posudomoechnye_mashiny/",
    "https://asko-russia.ru/catalog/dukhovye-shkafy/",
    "https://asko-russia.ru/catalog/kompaktnye-dukhovye-shkafy/",
    "https://asko-russia.ru/catalog/varochnye-paneli/",
    "https://asko-russia.ru/catalog/vytyazhki/",
    "https://asko-russia.ru/catalog/kholodilniki/",
    "https://asko-russia.ru/catalog/kofemashiny/",
    "https://asko-russia.ru/catalog/mikrovolnovye_pechi/",
    "https://asko-russia.ru/catalog/podogrevateli_posudy/",
    "https://asko-russia.ru/catalog/vakuumatory/",
    "https://asko-russia.ru/catalog/complects-asko/",
    "https://asko-russia.ru/catalog/aksessuary/"
]

start_time = datetime.now()


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: requests.sessions.Session) -> str:
    """
    :param url: str
    :param headers: dict
    :param session: requests.sessions.Session
    :return: str
    """

    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


# Получаем количество страниц
def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(
            soup.find('ul', class_='pages-nav__list').find_all('li', class_='pages-nav__item')[-2].find_next().text)
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


def get_image_urls(headers):
    session = requests.Session()

    url = "https://asko-russia.ru/catalog/stiralnye_mashiny/stiralnaya-mashina-asko-w6098x-w-3.html"

    html = get_html(url=url, headers=headers, session=session)

    soup = BeautifulSoup(html, 'lxml')

    links = soup.find_all('a', class_='product-page-card__slider-link')

    for item in links:
        url = 'https://asko-russia.ru/' + item.get('href')

        if '.jpg' in url:
            print(url)


def main():
    pass

    # html = get_html(url=category_urls_list[0], headers=headers, session=session)

    # pages = get_pages(html=html)

    # print(pages)


if __name__ == '__main__':
    main()
