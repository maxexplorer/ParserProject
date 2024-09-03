import os
import time
from datetime import datetime

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

category_urls_list = [
    "https://bellodeco.ru/plintus-napolnyj/",
    "https://bellodeco.ru/stenovye-paneli/",
    "https://bellodeco.ru/moldingi/",
    "https://bellodeco.ru/karnizy/",
    "https://bellodeco.ru/ugly/",
    "https://bellodeco.ru/ekstruzionnyj-plintus/",
    "https://bellodeco.ru/nalichnik/",
    "https://bellodeco.ru/dekorativnye-elementy/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/128.0.0.0 Safari/537.36'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(ex)


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('div', class_='b-pageline').find_all('a')[-3].text.strip())
    except Exception:
        pages = 1

    return pages


def get_products_urls(category_urls_list, headers):
    count_urls = len(category_urls_list)

    products_urls_list = []

    with Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                product_url = f"{category_url}page/{page}/"
                try:
                    time.sleep(1)
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find('div', class_='catalogbox__wrapper').find_all('div', class_='catalogbox__title')
                    for item in data:
                        try:
                            product_url = f"https://bellodeco.ru/{item.find('a').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls_list.append(product_url)
                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

            print(f'Обработано: {i}/{count_urls}')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*products_urls_list, file=file, sep='\n')


def get_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(product_urls_list)

    result_list = []
    image_urls_list = []

    with Session() as session:
        for j, product_url in enumerate(product_urls_list, 1):
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
                image_data = soup.find('div', class_='newGall').find_all('li', class_='newGall__thumbItem')
                for img_url in image_data:
                    image_urls_list.append("https://decor-dizayn.ru" + img_url.find('img').get('full'))
            except Exception:
                image_data = None
            try:
                image_title = ' ,'.join(img_url.find('img').get('full').split('/')[-1] for img_url in image_data)
            except Exception:
                image_title = None

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
                price = soup.find('div', class_='price').text.strip()
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
    if not os.path.exists('images'):
        os.makedirs('images')

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, img_url in enumerate(image_urls_list, 1):
        image_title = img_url.split('/')[-1]

        with Session() as session:
            response = session.get(url=img_url)


        with open(f"images/{image_title}", "wb") as file:
            file.write(response.content)

        print(f'Обработано: {k}/{count_urls}')

# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('data'):
        os.makedirs('data')

    dataframe = DataFrame(data)

    with ExcelWriter('data/result_list.xlsx', mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data')

    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    get_urls(category_urls_list=category_urls_list, headers=headers)
    # result_list = get_data(file_path="data/product_urls_list.txt")
    # save_excel(data=result_list)
    # download_imgs(file_path="data/image_urls_list.txt")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
