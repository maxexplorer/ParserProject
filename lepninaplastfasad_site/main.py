import os
import time
from datetime import datetime
import re

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

category_urls_list = [
    "https://lepninaplastfasad.ru/catalog/karnizy/",
    "https://lepninaplastfasad.ru/catalog/moldingi/",
    "https://lepninaplastfasad.ru/catalog/podokonniki/",
    "https://lepninaplastfasad.ru/catalog/moldingi-tsokolnye/",
    "https://lepninaplastfasad.ru/catalog/zamki/",
    "https://lepninaplastfasad.ru/catalog/bossazhi/",
    "https://lepninaplastfasad.ru/catalog/pilyastry-sostavnye/",
    "https://lepninaplastfasad.ru/catalog/polukolonny-sostavnye/",
    "https://lepninaplastfasad.ru/catalog/kolonny-sostavnye/",
    "https://lepninaplastfasad.ru/catalog/elastichnaya-shpatlyevka/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
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
        print(f'get_html: {ex}')


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('div', class_='pages').find_all('a')[-1].text.strip())
    except Exception:
        pages = 1

    return pages


def get_products_urls(category_urls_list: list, headers: dict):
    category_count_urls = len(category_urls_list)

    products_urls_list = []
    processed_urls_set = set()

    with Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('div', class_='col-xl-3 col-lg-4 col-sm-6')
                    for item in data:
                        try:
                            item_url = item.find('button', class_='b2').get('onclick')

                            match = re.search(r"'(.*?)'", item_url)
                            if match:
                                short_url = match.group(1)
                            else:
                                continue

                            product_url = f"https://lepninaplastfasad.ru{short_url}"
                        except Exception:
                            continue

                        if product_url in processed_urls_set:
                            continue

                        products_urls_list.append(product_url)
                        processed_urls_set.add(product_url)
                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

                print(f'Обработано страниц: {page}/{pages}')

            if not os.path.exists('data'):
                os.makedirs('data')

            with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
                print(*products_urls_list, file=file, sep='\n')

            products_urls_list.clear()

            print(f'Обработано категорий: {i}/{category_count_urls}')


def get_products_data(file_path: str, headers: dict) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        products_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(products_urls_list)
    result_data = []
    images_urls_list = []

    with Session() as session:
        for j, product_url in enumerate(products_urls_list, 1):
            product_images_urls_list = []
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
                category = soup.find('ol', class_='breadcrumb__list').find_all('li', class_='breadcrumb__item')[
                    2].text.strip()
            except Exception:
                category = None

            try:
                data = soup.find('div', class_='page product')
            except Exception:
                continue

            try:
                sku = data.find('div', class_='product__art').text.strip()
            except Exception:
                sku = None

            try:
                title = data.find('h1', class_='product__title').text.strip()
            except Exception:
                title = None

            try:
                color = data.find('div', class_='product__color').text.strip()
            except Exception:
                color = None

            try:
                price = data.find('div', class_='price').find('span', class_='price__value').text.strip()
            except Exception:
                price = None

            try:
                images_items = soup.find('div', class_='product__main-photo').find_all('img')
                for image_item in images_items:
                    image_url = f"https://cosca.ru{image_item.get('src')}"
                    if image_url.lower().endswith(('.jpg', '.png', '.webp')):
                        images_urls_list.append(image_url)
                        product_images_urls_list.append(image_url)
                main_image_url = product_images_urls_list[0]
                additional_images_urls = '; '.join(product_images_urls_list[1:])
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                description = data.find('div', class_='product__descr').text.strip()
            except Exception:
                description = None

            result_dict = {
                'Ссылка': product_url,
                'Категория': category,
                'Артикул': sku,
                'Название товара': title,
                'Цвет': color,
                'Цена': price,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
                'Описание': description,
            }

            # Сбор параметров товара
            product_parameters = {}
            try:
                parameters_items = data.find('div', class_='param-tbl').find_all('div', class_='param-tbl__item')
                for parameter_item in parameters_items:
                    parameter_name = parameter_item.find('div', class_='param-tbl__param').text.strip()
                    parameter_value = parameter_item.find('div', class_='param-tbl__value').text.strip()
                    product_parameters[parameter_name] = parameter_value
            except Exception:
                pass

            result_dict.update(product_parameters)

            result_data.append(result_dict)

            print(f'Обработано товаров: {j}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/images_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*images_urls_list, file=file, sep='\n')

    return result_data


def download_imgs(file_path: str, headers: dict) -> None:
    if not os.path.exists('images'):
        os.makedirs('images')

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, image_url in enumerate(image_urls_list, 1):
        image_title = image_url.split('/')[-1]

        with Session() as session:
            time.sleep(1)
            response = session.get(url=image_url, headers=headers)

        with open(f"images/{image_title}", "wb") as file:
            file.write(response.content)

        print(f'Обработано изображений: {k}/{count_urls}')


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def get_unique_urls(file_path: str) -> None:
    # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
    with open(file_path, 'r', encoding='utf-8') as file:
        unique_urls = set(line.strip() for line in file)

    # Сохраняем уникальные URL-адреса обратно в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        print(*unique_urls, file=file, sep='\n')


def main():
    file_path_urls = "data/products_urls_list.txt"
    file_path_images = "data/images_urls_list.txt"

    try:
        # get_products_urls(category_urls_list=category_urls_list, headers=headers)

        result_data = get_products_data(file_path=file_path_urls, headers=headers)
        save_excel(data=result_data, species='products')

        get_unique_urls(file_path=file_path_images)
        download_imgs(file_path=file_path_images, headers=headers)
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
