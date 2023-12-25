import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()

url = "https://sm-rus.ru/"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://sm-rus.ru/smeg/duhovye-shkafy/",
    "https://sm-rus.ru/smeg/varochnye-paneli/",
    "https://sm-rus.ru/smeg/vytjazhki/",
    # "https://sm-rus.ru/smeg/sushilnye-mashiny/"
]


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


# Получаем количество страниц
def get_pages(html: str) -> int:
    """
    :param html: str
    :return: int
    """

    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(
            soup.find('ul', class_='pages-nav__list').find_all('li', class_='pages-nav__item')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки всех категорий товаров
def get_category_urls(url: str, headers: dict) -> list:
    """
    :param url: str
    :param headers: dict
    :return: list
    """

    category_urls_list = []

    with requests.Session() as session:
        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find('ul', class_='dropdown-menu js-dropdown').find_all('li')

            for item in data:
                category_url = f"https://sm-rus.ru{item.find('a').get('href')}"

                category_urls_list.append(category_url)

        except Exception as ex:
            print(ex)

        if not os.path.exists('data/categories'):
            os.makedirs('data/categories')

        with open(f'data/categories/category_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*category_urls_list, file=file, sep='\n')


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

            name_category = category_url.split('/')[-2]

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В категории {name_category}: {pages} страниц')

            for page in range(1, pages + 1):
                page_product_url = f"{category_url}/?PAGEN_7={page}"
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
                            product_url = f"https://sm-rus.ru{item.find('a', class_='card-type-and-title catalog-card__type-and-title').get('href')}"

                            item_info = item.find_all('li', class_='card-characteristics__list-item')[0].find('span', class_='card-characteristics__list-item-value').text.strip()

                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(
                            (product_url,
                             item_info)
                        )
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            print(f'Обработано: {i}/{count_urls} категорий')

            if not os.path.exists('data/products'):
                os.makedirs(f'data/products')

            with open(f'data/products/{name_category}.txt', 'w', encoding='utf-8') as file:
                print(*product_urls_list, file=file, sep='\n')


# Получаем данные о товарах
def get_data(file_path: str, headers: dict) -> list:
    """
    :param file_path: str
    :param headers: dict
    :return: list
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

    count = len(product_urls_list)

    print(f'Всего {count} товаров')

    result_list = []

    with requests.Session() as session:
        for i, product_url in enumerate(product_urls_list, 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                folder = soup.find('div', id='breadcrumbs').find_all('span', property='itemListElement')[
                    -2].text.strip()
            except Exception:
                folder = ''

            try:
                items = soup.find('div', id='product-title')
                name = f"{items.find('h1').text.strip()}/ Teka {items.find('h2').text.strip()}"
            except Exception:
                name = ''

            try:
                article = ''.join(
                    j for j in soup.find('div', id='ref-ean').find('div', class_='ref').text.strip() if j.isdigit())
            except Exception:
                article = ''
            try:
                price = ''.join(k for k in soup.find('div', id='product-pvpr').text.strip() if k.isdigit())
            except Exception:
                price = ''

            try:
                try:
                    image_data = soup.find('ul', id='product-img-max').find_all('li')
                    image = ''
                    for item in image_data:
                        url = item.find_next().get('data-normal')
                        if '.jpg' in url or '.png' in url or '.webp' in url:
                            image += f'{url}, '
                except Exception:
                    image = soup.find('span', class_='et_pb_image_wrap').find('img').get('data-normal')
            except Exception as ex:
                print(ex)
                image = ''

            try:
                description = ' '.join(soup.find('div', id='product-benefits-section').text.strip().split())
            except Exception:
                description = ''

            try:
                characteristics = ' / '.join(
                    item.text for item in soup.find('div', id='product-technical').find_all('li'))
            except Exception:
                characteristics = ''

            body = description + characteristics

            vendor = 'Teka'

            amount = 1

            result_list.append(
                (
                    vendor,
                    f"Teka/{folder}",
                    article,
                    name,
                    price,
                    image,
                    body,
                    amount,
                )
            )

            print(f'Обработано товаров: {i}/{count}')

    return result_list

def main():
    # get_category_urls(url=url, headers=headers)

    # get_product_urls(category_urls_list=category_urls_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
