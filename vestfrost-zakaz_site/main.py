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
    "https://www.vestfrost-zakaz.ru/shop/holodilniki-18c/",
    "https://www.vestfrost-zakaz.ru/shop/morozilniki-20c/",
    "https://www.vestfrost-zakaz.ru/shop/stiralnye-mashiny-25c",
    "https://www.vestfrost-zakaz.ru/shop/sushilnye-mashiny-69c/",
    "https://www.vestfrost-zakaz.ru/shop/posudomoechnye-mashiny-66c/",
    "https://www.vestfrost-zakaz.ru/shop/vinnye-shkafy-23c/",
    "https://www.vestfrost-zakaz.ru/shop/vstraivaemaya-tehnika-43c/",
    "https://www.vestfrost-zakaz.ru/shop/holodilnye-shkafy-24c/"
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


def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(
            soup.find('ul', class_='pagination pagination-lg').find_all('a', class_='page-link')[-2].find_next().text)
    except Exception:
        pages = 1

    return pages


def main():
    session = requests.Session()
    # html = get_html(url=category_urls_list[0], headers=headers, session=session)

    with open('data/source/index.html', 'r', encoding='utf-8') as file:
        html = file.read()

    pages = get_pages(html=html)

    print(pages)

    # if not os.path.exists:
    #     os.makedirs('data/source')
    #
    # with open('data/source/index.html', 'w', encoding='utf-8') as file:
    #     file.write(html)


if __name__ == '__main__':
    main()
