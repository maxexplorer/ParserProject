import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://www.teka.com/ru-ru/kuhni/duhovye-shkafy/",
    "https://www.teka.com/ru-ru/kuhni/mikrovolnovye-pechi/",
    "https://www.teka.com/ru-ru/kuhni/kofemashina/",
    "https://www.teka.com/ru-ru/kuhni/varochnye-poverhnosti/",
    "https://www.teka.com/ru-ru/kuhni/vytyazhki/",
    "https://www.teka.com/ru-ru/kuhni/holodilnoe-oborudovanie/",
    "https://www.teka.com/ru-ru/kuhni/holodilniki-dlya-vina/",
    "https://www.teka.com/ru-ru/kuhni/mojki/",
    "https://www.teka.com/ru-ru/kuhni/kuhonnye-smesiteli/",
    "https://www.teka.com/ru-ru/kuhni/posudomoechnye-mashiny/",
    "https://www.teka.com/ru-ru/kuhni/kuhonnye-aksessuary/",
    "https://www.teka.com/ru-ru/kuhni/zapasnye-chasti/",
    "https://www.teka.com/ru-ru/stirka/stiralnye-mashiny/",
    "https://www.teka.com/ru-ru/stirka/stirka-s-sushkoj/",
    "https://www.teka.com/ru-ru/izmelchiteli/",
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

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find_all('div', class_='productCat')
                for item in data:
                    try:
                        product_url = item.find('a').get('href')
                    except Exception as ex:
                        print(ex)
                        continue
                    product_urls_list.append(product_url)
            except Exception as ex:
                print(ex)

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


def save_csv(name, data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/results/{name}_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('vendor: Производитель',
             'folder: Категория',
             'article: Артикул',
             'name: Название',
             'price: Цена',
             'image: Иллюстрация',
             'body: Описание',
             'amount : Количество'
             )
        )

    with open(f'data/results/{name}_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    # get_product_urls(category_urls_list=category_urls_list, headers=headers)

    directory = 'data\products'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            name = file_path.split('\\')[-1].split('.')[0]
            print(f'Обрабатывается категория {name}')
            result_list = get_data(file_path=file_path, headers=headers)
            save_csv(name=name, data=result_list)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
