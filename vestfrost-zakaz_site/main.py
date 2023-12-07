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
    "https://www.vestfrost-zakaz.ru/shop/holodilniki-18c",
    "https://www.vestfrost-zakaz.ru/shop/morozilniki-20c",
    "https://www.vestfrost-zakaz.ru/shop/stiralnye-mashiny-25c",
    "https://www.vestfrost-zakaz.ru/shop/sushilnye-mashiny-69c",
    "https://www.vestfrost-zakaz.ru/shop/posudomoechnye-mashiny-66c",
    "https://www.vestfrost-zakaz.ru/shop/vinnye-shkafy-23c",
    "https://www.vestfrost-zakaz.ru/shop/vstraivaemaya-tehnika-43c",
    "https://www.vestfrost-zakaz.ru/shop/holodilnye-shkafy-24c"
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
            soup.find('ul', class_='pagination pagination-lg').find_all('a', class_='page-link')[-2].find_next().text)
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


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
        for i, category_url in enumerate(category_urls_list[7:], 1):
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
                product_url = f"{category_url}_{page}"
                try:
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{product_url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('div', class_='product_name')
                    for item in data:
                        try:
                            product_url = f"https://www.vestfrost-zakaz.ru{item.find('a').get('href')}"
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
        for i, product_url in enumerate(product_urls_list[:1], 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                folder = soup.find('div', class_='breadcrumbs', id='allspec').find_all(
                    'a', style='text-decoration:underline;')[-1].text.strip()
            except Exception:
                folder = ''

            try:
                article = soup.find('div', class_='review').find_next().find_next().text.strip()
            except Exception:
                article = ''

            try:
                name = soup.find('h1', class_='product-name').text.strip()
            except Exception:
                name = ''

            try:
                price = soup.find('div', class_='price').find('p', class_='text-right nowrap price-new').next.text.strip().replace(' ', '')
            except Exception:
                price = ''

            try:
                image_data = soup.find('div', class_='slick-list draggable')

                if image_data:
                    image = ''
                    for item in image_data:
                        try:
                            image_url = f"https://www.vestfrost-zakaz.ru{item.get('src')}"
                            print(image_url)
                            image += f'{image_url}, '
                        except Exception as ex:
                            print(ex)
                            continue

                else:
                    image = f"https://kuppersberg.ru{soup.find('picture', class_='prodMain__gallery__img').find('img').get('src')}"
            except Exception:
                image = ''

            # try:
            #     body = ' '.join(soup.find('div', class_='prodTabs__item__row grid').text.strip().split())
            # except Exception:
            #     body = ''
            #
            # amount = 1
            #
            # result_list.append(
            #     (folder,
            #      article,
            #      name,
            #      price,
            #      image,
            #      body,
            #      amount,
            #      )
            # )
            #
            # print(f'Обработано товаров: {i}/{count}')

    return result_list


def save_csv(name, data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data/results'):
        os.makedirs('data/results')

    with open(f'data/results/{name}_{cur_date}.csv', 'w', encoding='utf-8') as file:
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

    with open(f'data/results/{name}_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    # get_product_urls(category_urls_list, headers)

    directory = 'data\products'
    for filename in os.listdir(directory)[:1]:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            name = file_path.split('\\')[-1].split('.')[0]
            result_list = get_data(file_path=file_path, headers=headers)
            # save_csv(name=name, data=result_list)


if __name__ == '__main__':
    main()
