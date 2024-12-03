import json
import os
import re
import time
from datetime import datetime
from random import randint

from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_urls_list

start_time = datetime.now()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

processed_urls = set()

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
        pages = int(
            soup.find('ul', class_='s_paging__item pagination d-flex mb-2 mb-sm-3').find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_products_urls(category_urls_list: list, headers: dict, region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_arkonasports_{region}.txt'

    products_urls_set = set()

    with Session() as session:
        for category_name, category_url in category_urls_list:
            products_urls = []

            print(f'Обрабатывается категория: {category_name} url: {category_url}')

            try:
                time.sleep(randint(3, 5))
                html = get_html(url=category_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(0, pages):
                category_page_url = f"{category_url}?counter={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=category_page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{category_page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('section',
                                              class_='search products d-flex flex-wrap mb-2 mb-sm-3').find_all('div',
                                                                                                               class_='product col-6 col-sm-4 col-xl-3 pt-3 pb-md-3')
                    for product_item in product_items:
                        try:
                            product_url = product_item.find('a').get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)
                        products_urls_set.add(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page + 1}/{pages} страниц')

            get_products_data(products_urls=products_urls, headers=headers, region=region)

            print(f'Обработана категория: {category_name} url: {category_url}')

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'a', encoding='utf-8') as file:
            print(*products_urls_set, file=file, sep='\n')


# Функция получения данных товаров
def get_products_data(products_urls: list, headers: dict, region: str, get_version_urls=True) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_version_list_arkonasports_{region}.txt'

    result_data = []
    version_urls_set = set()

    count_urls = len(products_urls)

    print(f'Всего: {count_urls} товаров!')

    with Session() as session:
        for i, product_url in enumerate(products_urls, 1):
            try:
                time.sleep(randint(2, 4))
                html = get_html(url=product_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                product_id = product_url.split('-')[-1]
            except Exception:
                product_id = None

            try:
                category_list = soup.find('div', class_='list_wrapper')
                try:
                    product_name_original = category_list.find('li', class_='bc-active bc-product-name').text.strip()
                    product_name = translator(product_name_original)
                except Exception:
                    product_name = None

                try:
                    category_name = '/'.join(
                        category.text.strip() for category in category_list.find_all('a', class_='category'))
                except Exception:
                    category_name = None

            except Exception:
                pass

            try:
                data = soup.find('div', id='content')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                versions_items = data.find('div', class_='projector_versions__sub').find_all('option')

                for version_item in versions_items:
                    # Проверяем, есть ли у элемента атрибут 'selected'
                    if version_item.get('selected') is not None:
                        try:
                            category_size = version_item.text.strip()
                        except Exception:
                            category_size = None
                    elif get_version_urls:
                        try:
                            version_url = f"https://arkonasports.pl{version_item.get('data-link')}"
                        except Exception:
                            version_url = None
                        version_urls_set.add(version_url)
            except Exception:
                category_size = None

            try:
                brand = data.find('span', class_='dictionary__name_txt', string=re.compile('Brand')).find_next(
                    'a', class_='dictionary__value_txt').text.strip()
            except Exception:
                brand = True

            try:
                images_urls_list = []
                images_items = data.find('section', id='projector_photos').find_all('figure')
                for item in images_items:
                    try:
                        image_url = item.find('a').get('href')
                    except Exception:
                        image_url = None
                    if not image_url:
                        try:
                            image_url = item.find('a').get('src')
                        except Exception:
                            image_url = None
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                description_original = data.find('section', id='projector_longdescription').text.strip()
                description = translator(description_original)
            except Exception:
                description = None

            try:
                html_data = data.find('script', class_='ajaxLoad').text.strip()
                html = ''.join(i.strip() for i in html_data.splitlines())

                # Используем регулярное выражение, чтобы найти JSON
                # pattern = r'{"product_id".*'
                pattern = r'(?<=product_data\s=\s)(\{.*?\})(?=\s*var)'
                match = re.search(pattern, html)

                if match:
                    # json_str = match.group(0).rstrip(
                    #     " var  trust_level = '1'; </script>").strip().replace("'", '"')  # Извлекаем строку с JSON
                    json_str = match.group(0).replace("'", '"')
                    try:
                        # Преобразуем JSON-строку в Python-объект
                        product_dict = json.loads(json_str)
                    except json.JSONDecodeError as ex:
                        print(f'Ошибка при декодировании JSON: {ex} url: {product_url}')

                else:
                    print("JSON не найден")
            except Exception as ex:
                print(f'html_data: {ex}')

            try:
                sizes_dict = product_dict['sizes']
            except Exception:
                sizes_dict = {}

            for key, value in sizes_dict.items():
                try:
                    if category_size:
                        size = f"{category_size}/{value['name']}"
                    else:
                        size = value['name']
                except Exception:
                    size = None
                try:
                    quantity = value['amount']
                except Exception:
                    quantity = None
                if quantity:
                    status_size = 'в наличии'
                else:
                    status_size = 'нет в наличии'
                try:
                    price = value['price']['value']
                except Exception:
                    price = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': product_id,
                        'Название товара оригинальное': product_name_original,
                        'Название товара': product_name,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': price,
                        'НДС, %*': None,
                        'Включить продвижение': None,
                        'Ozon ID': product_id,
                        'Штрихкод (Серийный номер / EAN)': None,
                        'Вес в упаковке, г*': None,
                        'Ширина упаковки, мм*': None,
                        'Высота упаковки, мм*': None,
                        'Длина упаковки, мм*': None,
                        'Ссылка на главное фото*': main_image_url,
                        'Ссылки на дополнительные фото': additional_images_urls,
                        'Ссылки на фото 360': None,
                        'Артикул фото': None,
                        'Бренд в одежде и обуви*': brand,
                        'Объединить на одной карточке*': product_id,
                        'Цвет товара*': None,
                        'Российский размер*': size,
                        'Размер производителя': size,
                        'Статус наличия': status_size,
                        'Название цвета': None,
                        'Тип*': category_name,
                        'Пол*': None,
                        'Размер пеленки': None,
                        'ТН ВЭД коды ЕАЭС': None,
                        'Ключевые слова': None,
                        'Сезон': None,
                        'Рост модели на фото': None,
                        'Параметры модели на фото': None,
                        'Размер товара на фото': None,
                        'Коллекция': None,
                        'Страна-изготовитель': None,
                        'Вид принта': None,
                        'Аннотация': description,
                        'Инструкция по уходу': None,
                        'Серия в одежде и обуви': None,
                        'Материал': None,
                        'Состав материала': None,
                        'Материал подклада/внутренней отделки': None,
                        'Материал наполнителя': None,
                        'Утеплитель, гр': None,
                        'Диапазон температур, °С': None,
                        'Стиль': None,
                        'Вид спорта': None,
                        'Вид одежды': None,
                        'Тип застежки': None,
                        'Длина рукава': None,
                        'Талия': None,
                        'Для беременных или новорожденных': None,
                        'Тип упаковки одежды': None,
                        'Количество в упаковке': None,
                        'Состав комплекта': None,
                        'Рост': None,
                        'Длина изделия, см': None,
                        'Длина подола': None,
                        'Форма воротника/горловины': None,
                        'Детали': None,
                        'Таблица размеров JSON': None,
                        'Rich-контент JSON': None,
                        'Плотность, DEN': None,
                        'Количество пар в упаковке': None,
                        'Класс компрессии': None,
                        'Персонаж': None,
                        'Праздник': None,
                        'Тематика карнавальных костюмов': None,
                        'Признак 18+': None,
                        'Назначение спецодежды': None,
                        'HS-код': None,
                        'Количество заводских упаковок': None,
                        'Ошибка': None,
                        'Предупреждение': None,
                    }
                )

            print(f'Обработано: {i}/{count_urls} товаров!')

        save_excel(data=result_data, region=region)

        if get_version_urls:
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, 'a', encoding='utf-8') as file:
                print(*version_urls_set, file=file, sep='\n')


# Функция для записи данных в формат xlsx
def save_excel(data: list, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_products_arkonasports_{region}.xlsx'

    # Если файл не существует, создаем его с пустым DataFrame
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    # driver = init_chromedriver(headless_mode=True)

    value = input('Введите значение:\n1 - Германия\n2 - Турция\n3 - Польша\n')

    if value == '1':
        region = 'Германия'
        base_currency = 'EUR'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс EUR/RUB: {currency}')

    elif value == '2':
        region = 'Турция'
        base_currency = 'TRY'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс TRY/RUB: {currency}')

    elif value == '3':
        region = 'Польша'
        base_currency = 'PLN'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс PLN/RUB: {currency}')
        get_products_urls(category_urls_list=category_urls_list_pl, headers=headers, region=region)

        # Путь к файлу для сохранения URL продуктов
        directory = 'data'
        file_path_product_list = f'{directory}/url_products_list_arkonasports_{region}.txt'
        file_path_version_list = f'{directory}/url_version_list_arkonasports_{region}.txt'

        # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
        with open(file_path_product_list, 'r', encoding='utf-8') as file:
            product_urls = set(line.strip() for line in file)

        # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
        with open(file_path_version_list, 'r', encoding='utf-8') as file:
            version_urls = set(line.strip() for line in file)

        # Выбираем URL, которые находятся в version_urls, но не в product_urls
        unique_urls_list = list(version_urls - product_urls)

        if unique_urls_list:
            # Сохраняем уникальные URL-адреса обратно в файл
            with open(file_path_product_list, 'a', encoding='utf-8') as file:
                print(*unique_urls_list, file=file, sep='\n')

            print(f'Получено {len(unique_urls_list)} дополнительных версий товаров!')
            get_products_data(products_urls=unique_urls_list, headers=headers, region=region, get_version_urls=False)

    else:
        raise ValueError('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
