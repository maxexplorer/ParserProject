import os
import time
from datetime import datetime

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
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


def get_products_urls(category_urls_list: list, headers: dict) -> list:
    count_urls = len(category_urls_list)

    new_products_urls_list = []

    with open('data/exception_urls_list.txt', 'r', encoding='utf-8') as file:
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

                        if product_url in exception_urls_list:
                            continue
                        new_products_urls_list.append(product_url)

                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

            print(f'Обработано: {i}/{count_urls}')

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
                title = soup.find('h1').text.strip()
            except Exception:
                title = None

            try:
                price = int(
                    ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='catalogbox__price').text.strip())))
            except Exception:
                price = None

            try:
                images_items = soup.find('div', class_='catalogbox__galbox js-catalog-detail-fotorama-wrap').find_all(
                    'a')
                for image_item in images_items:
                    image_url = f"https://bellodeco.ru/{image_item.get('href')}"
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list[1:])
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                description = soup.find('div', class_='catalogbox__description').text.strip().splitlines()[-1]
            except Exception:
                description = None

            try:
                models = soup.find('div', class_='b-model-list').find_all('div', class_='model-list__item')
                try:
                    model_fbx = models[0].find('a').get('href')
                except Exception:
                    model_fbx = None
                try:
                    model_obj = models[1].find('a').get('href')
                except Exception:
                    model_obj = None
                try:
                    model_3ds = models[2].find('a').get('href')
                except Exception:
                    model_3ds = None
            except Exception:
                pass

            result_dict = {
                'Название товара': title,
                'Ссылка': product_url,
                'Цена': price,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
                'Описание': description,
                'Модель fbs': model_fbx,
                'Модель obj': model_obj,
                'Модель 3ds': model_3ds,
            }

            # Сбор параметров товара
            product_parameters = {}
            try:
                parameters_items = soup.find('div', class_='catalogbox__param__left').find_all('div')
                for parameter_item in parameters_items:
                    attribute_name = parameter_item.text.split(':')[0].strip()
                    attribute_value = parameter_item.text.split(':')[1].strip()
                    product_parameters[attribute_name] = attribute_value
            except Exception:
                pass

            # Сбор характеристик товара
            product_characteristics = {}
            try:
                characteristics_items = soup.find('div', id='tabs-obj_description').find_all('tr')
                for characteristic_item in characteristics_items:
                    characteristic = characteristic_item.find_all('td')
                    attribute_name = characteristic[0].text.strip()
                    attribute_value = characteristic[1].text.strip()
                    product_characteristics[attribute_name] = attribute_value
            except Exception:
                pass

            product_attributes = {**product_parameters, **product_characteristics}

            result_dict.update(product_attributes)

            result_data.append(result_dict)

            print(f'Обработано: {j}/{count_urls}')

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

            # try:
            #     title = soup.find('h1').text.strip()
            # except Exception:
            #     title = None

            try:
                price = int(
                    ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='catalogbox__price').text.strip())))
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

    for k, img_url in enumerate(image_urls_list, 1):
        image_title = img_url.split('/')[-1]

        with Session() as session:
            time.sleep(1)
            response = session.get(url=img_url, headers=headers)

        with open(f'{directory}/{image_title}', 'wb') as file:
            file.write(response.content)

        print(f'Обработано: {k}/{count_urls}')


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


def main():
    # Считываем Excel-файл
    excel_data = read_excel('data/data.xlsx', sheet_name=0)  # sheet_name=0 для первой страницы

    # Преобразуем в список списков
    data_list = excel_data.values.tolist()

    # Собираем цены товаров
    result_data_price = get_products_price(products_urls_list=data_list, headers=headers)
    save_excel(data=result_data_price, species='price')

    # Собираем новые URL
    new_products_urls_list = get_products_urls(category_urls_list=category_urls_list, headers=headers)

    if new_products_urls_list:
        result_data_products = get_products_data(products_urls_list=new_products_urls_list, headers=headers)
        save_excel(data=result_data_products, species='products')
        download_imgs(file_path="data/images_urls_list.txt", headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
