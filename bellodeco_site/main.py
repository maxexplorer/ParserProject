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
                    print(f"{product_url} - {ex}")
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

    with open('data/products_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*products_urls_list, file=file, sep='\n')


def get_products_data(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        products_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(products_urls_list)

    result_list = []
    images_urls_list = []

    with Session() as session:
        for j, product_url in enumerate(products_urls_list[:1], 1):
            try:
                time.sleep(1)
                html = get_html(url=product_url, headers=headers, session=session)
                #
                # with open('data/index.html', 'w', encoding='utf-8') as file:
                #     file.write(html)

            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                title = soup.find('h1').text.strip()
            except Exception:
                title = None

            try:
                price = int(''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='catalogbox__price').text.strip())))
            except Exception:
                price = None

            try:
                images_items = soup.find('div', class_='catalogbox__galbox js-catalog-detail-fotorama-wrap').find_all('a')
                for image_item in images_items:
                    image_url = f"https://bellodeco.ru/{image_item.get('href')}"
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                description = soup.find('div', class_='catalogbox__description').text.strip().splitlines()[-1]
            except Exception:
                description = None

            try:
                models = soup.find('div', class_='b-model-list').find_all('div', class_='model-list__item')
            except Exception:
                models = None



            try:
                data = soup.find('div', class_='data').find_all('div', class_='item')
            except Exception:
                data = None

            result_dict = {
                'Название товара': title,
                'Ссылка': product_url,
                'Цена': price,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
                'Описание': description,
                '3D модели': models,


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
        print(*images_urls_list, file=file, sep='\n')

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
    # get_products_urls(category_urls_list=category_urls_list, headers=headers)
    result_list = get_products_data(file_path="data/products_urls_list.txt")
    # save_excel(data=result_list)
    # download_imgs(file_path="data/image_urls_list.txt")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
