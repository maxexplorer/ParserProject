import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import json
from pandas import DataFrame, ExcelWriter
import openpyxl

start_time = datetime.now()

category_urls_list = [
    "https://decor-dizayn.ru/catalog/belaya-lepnina/karnizy-belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/moldingi_belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/plintusy_belye/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/ugolki_belie/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/pilyastry/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/dekorativnye-elementi/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/paneli/",
    "https://decor-dizayn.ru/catalog/belaya-lepnina/skrytoe-osveshchenie/",
    "https://decor-dizayn.ru/catalog/rashodnye-materiali/kley/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/tsvetniye_plintusy/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dekorativnye-reyki/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/neo-klassika/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/afrodita/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/mramor/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/sultan/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/khay-tek/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dykhanie-2/",
    "https://decor-dizayn.ru/catalog/tsvetnaya-lepnina/dykhanie-vostoka/"
]

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='pages').find_all('a')[-1].get('href').split('=')[-1])
    except Exception:
        pages = 1
    return pages


def get_urls(category_urls_list, headers):
    count_urls = len(category_urls_list)

    product_urls_list = []

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                product_url = f"{category_url}?PAGEN_1={page}"
                try:
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find('div', class_='types').find_next().find_next().find_next().find_all(class_='item')
                    for item in data:
                        try:
                            url = "https://decor-dizayn.ru" + item.find(class_='image').get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(url)
                except Exception as ex:
                    print(ex)

            print(f'Обработано: {i}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*product_urls_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(product_urls_list)

    result_list = []
    image_urls_list = []

    with requests.Session() as session:
        for j, product_url in enumerate(product_urls_list[:10], 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                title = soup.find('h2', class_='product_name').text.strip()
            except Exception:
                title = None
            try:
                image_title = ' ,'.join(img_url.find('img').get('src').split('/')[-1] for img_url in image_data)
            except Exception:
                image_title = None
            try:
                image_data = soup.find('div', class_='newGall').find_all('li', class_='newGall__thumbItem')
                for img_url in image_data:
                    image_urls_list.append("https://decor-dizayn.ru" + img_url.find('img').get('src'))
            except Exception:
                image_data = None
            try:
                description = soup.find('div', id='t1').text.strip().splitlines()[-1]
            except Exception:
                description = None
            try:
                models = ' ,'.join(["https://decor-dizayn.ru" + model.get('href') for model in
                                    soup.find('div', id='t4').find_all('a')])
            except Exception:
                models = None
                pass
            try:
                price = soup.find('div', class_='price').text.strip().split()[0]
            except Exception:
                price = None

            try:
                data = soup.find('div', class_='data').find_all('div', class_='item')
            except Exception:
                data = None

            result_dict = {
                'Название товара': title,
                'Ссылка': product_url,
                'Изображения': image_title,
                'Описание': description,
                '3D модели': models,
                'Цена': price,

            }

            info_list = []

            for item in data:
                info_list.append(item.text.strip().splitlines())
            info_dict = dict(info_list)

            result_dict.update(info_dict)

            result_list.append(result_dict)

            print(f'Обработано: {j}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/image_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*image_urls_list, file=file, sep='\n')

    return result_list

def download_imgs(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, img_url in enumerate(image_urls_list, 1):
        image_title = img_url.split('/')[-1]

        response = requests.get(url=img_url)

        if not os.path.exists('images'):
            os.mkdir('images')

        with open(f"images/{image_title}.jpg", "wb") as file:
            file.write(response.content)

        print(f'Обработано: {k}/{count_urls}')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    # get_urls(category_urls_list=category_urls_list, headers=headers)
    result_list = get_data(file_path="data/product_urls_list.txt")
    save_excel(data=result_list)
    download_imgs(file_path="data/image_urls_list.txt")
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
