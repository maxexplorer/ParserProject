import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()


url = "https://www.mql5.com/ru/signals"
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

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

        if response.status_code != 200:
            print(f'{url}: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(ex)


def main():

    # session = requests.Session()

    # html = get_html(url=url, headers=headers, session=session)

    # with open('data/index.html', 'w', encoding='utf-8') as file:
    #     file.write(html)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()

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

if __name__ == '__main__':
    main()