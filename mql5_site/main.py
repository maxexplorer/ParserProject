import time

import requests
import os
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from random import randint
from datetime import datetime

start_time = datetime.now()

url = "https://www.mql5.com/ru/signals"
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


def auth_requests():

    cookies = {
        'lang': 'ru',
        '_fz_uniq': '5092989988158047822',
        'sid': 'CfDJ8FnDEf3cAqtAi8dm607EzngSc7SjPnDrrFrEmJNzs8nlUsN54QCQZqh2SA3iwkgKhx%2BKM8qgNs0dnrNrJaP%2BmH%2BWnrocuUKmNIyFu8rz5G%2B3w2xL9YQBymqyNqMVX5NMUhAre5WNJDyS%2Bn%2Bl3lZiF4oQONgiCxGV4Z5ADheJ03TH',
        '_fz_fvdt': '1701614673',
        'utm_source': 'www.mql5.com',
        'utm_campaign': '509.ru.password.recovery',
        '_fz_ssn': '1702215185005830593',
        '_media_uuid': '2218201859',
    }

    headers = {
        'authority': 'www.mql5.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': 'lang=ru; _fz_uniq=5092989988158047822; sid=CfDJ8FnDEf3cAqtAi8dm607EzngSc7SjPnDrrFrEmJNzs8nlUsN54QCQZqh2SA3iwkgKhx%2BKM8qgNs0dnrNrJaP%2BmH%2BWnrocuUKmNIyFu8rz5G%2B3w2xL9YQBymqyNqMVX5NMUhAre5WNJDyS%2Bn%2Bl3lZiF4oQONgiCxGV4Z5ADheJ03TH; _fz_fvdt=1701614673; utm_source=www.mql5.com; utm_campaign=509.ru.password.recovery; _fz_ssn=1702215185005830593; _media_uuid=2218201859',
        'origin': 'https://www.mql5.com',
        'referer': 'https://www.mql5.com/ru/auth_login',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    data = {
        'RedirectAfterLoginUrl': 'https://www.mql5.com/ru/signals',
        'RegistrationUrl': '',
        'ShowOpenId': 'True',
        'ViewType': '0',
        'Login': 'Maxexplorer',
        'Password': '',
        'signature': '1fd19bf6ad495198af6ac73c5e5f5567d6fe18ebdb52646e39aeaa2e398e57b5',
    }

    response = requests.post('https://www.mql5.com/ru/auth_login', cookies=cookies, headers=headers, data=data)

    print(response.text)

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


# Получаем количество страниц
def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='paginatorEx').find_all('a', rel='nofollow')[-1].text)
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки товаров
def get_card_urls(headers: dict, meta_trader: str) -> None:
    """
    :param headers: dict
    :param meta_trader: str
    :return: None
    """

    with requests.Session() as session:
        card_urls_list = []

        try:
            html = get_html(url=f"https://www.mql5.com/ru/signals/{meta_trader}/page1", headers=headers, session=session)
        except Exception as ex:
            pages = 30
            print(f'Не удалось получить HTML страницы для получения количества страниц. Будет использовано значение '
                  f'по умолчанию: {pages}')
        else:
            pages = get_pages(html=html)

        print(f'Всего: {pages} страниц')

        for page in range(1, pages + 1):
            time.sleep(randint(1, 3))

            useragent = UserAgent()

            page_card_url = f"https://www.mql5.com/ru/signals/{meta_trader}/page{page}"

            headers = {
                'Accept': '*/*',
                'User-Agent': useragent.random
            }

            try:
                html = get_html(url=page_card_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{page_card_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find_all('a', class_='signal-card__wrapper')
                for item in data:
                    try:
                        card_url = f"https://www.mql5.com{item.get('href')}"
                    except Exception as ex:
                        print(ex)
                        continue
                    card_urls_list.append(card_url)

            except Exception as ex:
                print(ex)

            print(f'Обработано: {page}/{pages} страниц')

        if not os.path.exists('data/cards'):
            os.makedirs(f'data/cards')

        with open(f'data/cards/card_urls_list_{meta_trader}.txt', 'w', encoding='utf-8') as file:
            print(*card_urls_list, file=file, sep='\n')


# Получаем данные о товарах
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        card_urls_list = [line.strip() for line in file.readlines()]

    count = len(card_urls_list)

    print(f'Всего {count} карточек')

    result_list = []

    # with requests.Session() as session:
    #     for i, product_url in enumerate(card_urls_list[:1], 1):
    #
    #         if i % 10 == 0:
    #             useragent = UserAgent()
    #
    #             headers = {
    #                 'Accept': '*/*',
    #                 'User-Agent': useragent.random
    #             }
    #
    #         try:
    #             html = get_html(url=product_url, headers=headers, session=session)
    #         except Exception as ex:
    #             print(f"{product_url} - {ex}")
    #             continue
    #
    #         with open('data/index.html', 'w', encoding='utf-8') as file:
    #             file.write(html)

    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()



    soup = BeautifulSoup(html, 'lxml')


    # print(f'Обработано карточек: {i}/{count}')


def save_csv(data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/results/{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('folder: Категория',
             'article: Артикул',
             'name: Название',
             'price: Цена',
             'image: Иллюстрация',
             'body: Описание',
             'amount : Количество',
             )
        )

    with open(f'data/results/{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    # meta_trader = 'mt5'
    #
    # get_card_urls(headers=headers, meta_trader=meta_trader)
    #
    # get_data(file_path='data/cards/card_urls_list.txt', headers=headers)
    #
    # execution_time = datetime.now() - start_time
    # print('Сбор данных завершен!')
    # print(f'Время работы программы: {execution_time}')

    auth_requests()


if __name__ == '__main__':
    main()
