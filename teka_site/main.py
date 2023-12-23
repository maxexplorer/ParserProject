import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()

url = "https://www.teka.com/ru-ru/kuhni/duhovye-shkafy/"

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
            print(response.status_code)

        html = response.text
        return html
    except Exception as ex:
        print(ex)


# Получаем ссылки товаров
def get_product_urls(category_urls_list: list, headers: dict) -> None:
    """
    :param file_path: list
    :param headers: dict
    :return: None
    """

    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            product_urls_list = []

            name_category = category_url.split('/')[-1]

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find('div', class_='et_pb_portfolio_grid_items product-list').find_all('div',
                                                                                                   class_='productCat')
                for item in data:
                    try:
                        product_url = item.find('a').get('href')
                        print(product_url)
                    except Exception as ex:
                        print(ex)
                        continue
                    product_urls_list.append(product_url)
            except Exception as ex:
                print(ex)

        # print(f'Обработано: {i}/{count_urls} категорий')
        #
        # if not os.path.exists('data/products'):
        #     os.makedirs(f'data/products')
        #
        # with open(f'data/products/{name_category}.txt', 'w', encoding='utf-8') as file:
        #     print(*product_urls_list, file=file, sep='\n')


def main():
    session = requests.Session()

    html = get_html(url=url, headers=headers, session=session)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
