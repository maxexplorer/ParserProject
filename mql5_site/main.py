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

# Получаем ссылки товаров
def get_product_urls(headers: dict) -> None:
    """
    :param headers: dict
    :return: None
    """

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            product_urls_list = []

            name_category = category_url.split('/')[-1]

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В категории {name_category}: {pages} страниц')

            for page in range(1, pages + 1):
                page_product_url = f"{category_url}/?PAGEN_6={page}"
                try:
                    html = get_html(url=page_product_url, headers=headers, session=session)

                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('div', class_='catalog-card__text-content')
                    for item in data:
                        try:
                            product_url = f"https://asko-russia.ru{item.find('a').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            print(f'Обработано: {i}/{count_urls} категорий')

            if not os.path.exists('data/products'):
                os.makedirs(f'data/products')

            with open(f'data/products/{name_category}.txt', 'w', encoding='utf-8') as file:
                print(*product_urls_list, file=file, sep='\n')

if __name__ == '__main__':
    main()