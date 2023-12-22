import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()

url = "https://evelux.ru/catalog/"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

category_urls_list = [
    "https://evelux.ru/catalog/aksessuary/additional-accessories/",
    "https://evelux.ru/catalog/aksessuary/soedinitelnye-elementy/",
    "https://evelux.ru/catalog/aksessuary/filtry/",
    "https://evelux.ru/catalog/vstraivaemaya/dukhovye-shkafy/?FILTER=DSHGAS",
    "https://evelux.ru/catalog/vstraivaemaya/dukhovye-shkafy/?FILTER=DSHELECTRO",
    "https://evelux.ru/catalog/vstraivaemaya/varochnye-poverkhnosti/?FILTER=GAZ",
    "https://evelux.ru/catalog/vstraivaemaya/varochnye-poverkhnosti/?FILTER=ELECTRO",
    "https://evelux.ru/catalog/vstraivaemaya/varochnye-poverkhnosti/?FILTER=INDUCTION",
    "https://evelux.ru/catalog/vstraivaemaya/vytyazhki/",
    "https://evelux.ru/catalog/vstraivaemaya/posudomoechnye-mashiny/",
    "https://evelux.ru/catalog/vstraivaemaya/mikrovolnovye-pechi/",
    "https://evelux.ru/catalog/vstraivaemaya/stiralnye-mashiny/",
    "https://evelux.ru/catalog/vstraivaemaya/kholodilniki/",
    "https://evelux.ru/catalog/komplekty/",
    "https://evelux.ru/catalog/otdelnostoyashaja/stiralnye-mashiny-solo/",
    "https://evelux.ru/catalog/otdelnostoyashaja/sushilnye-mashiny/",
    "https://evelux.ru/catalog/otdelnostoyashaja/kholodilniki-solo/",
    ""
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

            name_category = category_url.split('/')[-1]

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            for page in range(1, 2):
                page_product_url = f"{category_url}"
                try:
                    html = get_html(url=page_product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('div', class_='goods__item-slider owl-carousel owl-theme')

                    for item in data:
                        try:
                            product_url = f"{page_product_url}/{item.find('a').get('href')}"
                            print(product_url)
                        except Exception as ex:
                            print(ex)
                            continue
                        # product_urls_list.append(product_url)
                except Exception as ex:
                    print(ex)

                # print(f'Обработано: {page}/{pages} страниц')

            # print(f'Обработано: {i}/{count_urls} категорий')

            # if not os.path.exists('data/products'):
            #     os.makedirs(f'data/products')
            #
            # with open(f'data/products/{name_category}.txt', 'w', encoding='utf-8') as file:
            #     print(*product_urls_list, file=file, sep='\n')


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
    category_urls_list = ["https://evelux.ru/catalog/vstraivaemaya/dukhovye-shkafy/?FILTER=DSHELECTRO"]

    get_product_urls(category_urls_list=category_urls_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
