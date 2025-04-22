import os
import time
from datetime import datetime
import re

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

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



def get_products_urls(category_urls_list: list, headers: dict) -> list:
    count_urls = len(category_urls_list)

    new_products_urls_list = []

    with open('data/exceptions_urls_list.txt', 'r', encoding='utf-8') as file:
        exception_urls_list = [line.strip() for line in file]

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
                        except Exception as ex:
                            print(f'{product_url}: {ex}')
                            continue

                        if product_url in exception_urls_list:
                            continue
                        new_products_urls_list.append(product_url)
                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

                print(f'Обработано страниц: {page}/{pages}')

            print(f'Обработана категория {category_url}: {i}/{count_urls}')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
        print(*new_products_urls_list, file=file, sep='\n')

    return new_products_urls_list


def get_products_data(products_urls_list: list, headers: dict) -> list[dict]:
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
                data = soup.find('div', class_='item-page')
            except Exception:
                continue

            try:
                name = data.find('h1').find('br').next.text.strip()
            except Exception:
                name = None

            try:
                sku = data.find('h1').find('span').text.strip()
            except Exception:
                sku = None

            if name and sku:
                title = f'{name} {sku}'
            else:
                title = name

            try:
                price = data.find('div', class_='price').find('span').text.strip()
            except Exception:
                price = None

            try:
                images_items = soup.find('div', class_='photo').find_all('img')
                for image_item in images_items:
                    image_url = f"https://lepninaplastfasad.ru{image_item.get('src')}"
                    if image_url.lower().endswith(('.jpg', '.png', '.webp')):
                        images_urls_list.append(image_url)
                        product_images_urls_list.append(image_url)
                main_image_url = product_images_urls_list[0]
                additional_images_urls = '; '.join(product_images_urls_list[1:])
            except Exception:
                main_image_url = None
                additional_images_urls = None

            result_dict = {
                'Ссылка': product_url,
                'Код товара': sku,
                'Название товара': title,
                'Цена': price,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
            }

            # Сбор параметров товара
            product_parameters = {}
            try:
                parameters_items = data.find('table').find_all('tr')
                for parameter_item in parameters_items:
                    parameter_item_td = parameter_item.find_all('td')
                    parameter_name = parameter_item_td[0].text.strip()
                    parameter_value = parameter_item_td[1].text.strip()
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


def get_products_price(products_urls_list: list, headers: dict) -> list[dict]:
    count_urls = len(products_urls_list)
    count = 1
    result_data = []

    with Session() as session:
        for title, product_url in products_urls_list:
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
                price = soup.find('div', class_='price').find('span').text.strip()
            except Exception:
                price = None

            result_data.append(
                {
                    'Название товара': title,
                    'Ссылка': product_url,
                    'Цена': price,
                }
            )

            print(f'Обработано: {count}/{count_urls}')
            count += 1

    return result_data


def download_imgs(file_path: str, headers: dict) -> None:
    directory = 'images'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, image_url in enumerate(image_urls_list, 1):
        image_title = image_url.split('/')[-1]

        with Session() as session:
            time.sleep(1)
            response = session.get(url=image_url, headers=headers)

        with open(f'{directory}/{image_title}', 'wb') as file:
            file.write(response.content)

        print(f'Обработано изображений: {k}/{count_urls}')


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    cur_date = datetime.now().strftime('%d-%m-%Y')

    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{species}_{cur_date}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    try:
        # Считываем Excel-файл
        excel_data = read_excel('data/data.xlsx', sheet_name=0, header=None)  # sheet_name=0 для первой страницы

        # Преобразуем в список списков
        data_list = excel_data.values.tolist()

        # Собираем цены товаров
        result_data_price = get_products_price(products_urls_list=data_list, headers=headers)
        save_excel(data=result_data_price, species='price')

        # Собираем новые URL
        new_products_urls_list = get_products_urls(category_urls_list=category_urls_list, headers=headers)

        if new_products_urls_list:
            print(f'Получено {len(new_products_urls_list)} новых товаров!')
            result_data_products = get_products_data(products_urls_list=new_products_urls_list, headers=headers)
            save_excel(data=result_data_products, species='products')
            download_imgs(file_path="data/images_urls_list.txt", headers=headers)
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
