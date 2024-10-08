import json
import os
from random import randint
import time
from datetime import datetime
from math import ceil

from requests import Session

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_urls_list_pl
from data.data import id_region_dict

from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}


# Функция инициализации объекта chromedriver
def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless_mode:
        options.add_argument("--headless=new")
    driver = Chrome(options=options)
    if not headless_mode:
        driver.maximize_window()
    driver.implicitly_wait(15)

    return driver


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
        pages_list = list(map(int, filter(lambda x: x.isdigit(),
                                          soup.find('div', class_='catalog-product-list__total-count').text.split())))
        if len(pages_list) == 2:
            pages = ceil(pages_list[1] / 48) + 1
        else:
            pages = 1
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_products_urls(driver: Chrome, category_urls_list: list, headers: dict, region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_{region}.txt'

    with Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            products_urls = []

            print(f'Обрабатывается категория: {category_url}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                category_page_url = f"{category_url}?page={page}"
                try:
                    driver.get(url=category_page_url)
                    driver.execute_script("window.scrollTo(0, 2000);")
                    time.sleep(1)
                    # driver.execute_script("window.scrollTo(0, 4000);")
                    # time.sleep(1)
                    html = driver.page_source
                except Exception as ex:
                    print(f"{category_page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('div', class_='plp-product-list__products').find_all('div',
                                                                                                   class_='plp-fragment-wrapper')
                    for product_item in product_items:
                        try:
                            product_url = product_item.find('a').get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, 'a', encoding='utf-8') as file:
                print(*products_urls, file=file, sep='\n')

            get_products_data(products_urls=products_urls, headers=headers, region=region)

            print(f'Обработано: {category_url}')


# Функция получения данных товаров
def get_products_data(products_urls: list, headers: dict, region: str) -> None:
    result_data = []

    count_urls = len(products_urls)

    print(f'Всего: {count_urls} товаров!')

    with Session() as session:
        for i, product_url in enumerate(products_urls, 1):
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
                data = soup.find('main', id='content')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                id_product = data.find('span', class_='pip-product-identifier__value').text.strip()
            except Exception:
                id_product = None

            try:
                name = data.find('h1').text.strip()
                name_item = name.split()[0]
                product_name = f'IKEA {name_item} {translator(name).lower()}'
            except Exception:
                product_name = None

            try:
                price = data.find('span', class_='pip-temp-price__integer').text.strip()
            except Exception:
                price = None

            try:
                color_original = data.find('span', class_='pip-list-view-item__addon').text.strip().lower()
            except Exception:
                color_original = None

            try:
                images_urls_list = []
                images_items = data.find('div', class_='pip-product-gallery__thumbnails').find_all('button')
                for item in images_items:
                    image_url = item.find('img').get('src').split('?')[0]
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                print('not images')
                main_image_url = None
                additional_images_urls = None

            try:
                description_original = ' '.join(
                    item.text for item in data.find('div', class_='pip-product-details__container').find_all('p'))
                description = translator(description_original)
            except Exception:
                description = None

            try:
                product_information_json = data.find('div',
                                                     class_='js-product-information-section pip-product-information-section').get(
                    'data-initial-props')

                product_information_dict = json.loads(product_information_json)
            except Exception:
                product_information_dict = None

            if product_information_dict:
                # try:
                #     product_sizes_original = ' '.join(
                #         item.text for item in
                #         data.find('div', class_='pip-product-dimensions__dimensions-container').find_all('p'))
                #     product_sizes = translator(product_sizes_original)
                # except Exception as ex:
                #     product_sizes = None

                try:
                    product_dimensions = {dict_item['name']: dict_item['measure'] for dict_item in
                                          product_information_dict['dimensionProps']['dimensions']}

                except Exception:
                    product_dimensions = None

                try:
                    packaging_dimensions = {dict_item['label']: dict_item['text'] for dict_item in
                                            product_information_dict['dimensionProps']['packaging']['contentProps'][
                                                'packages'][0]['measurements'][0]}

                    print(packaging_dimensions)
                except Exception:
                    packaging_dimensions = None

            brand = 'IKEA'
            subcategory_name = 'Текстиль'

            result_data.append(
                {
                    '№': None,
                    'Артикул': id_product,
                    'Название товара': product_name,
                    'Цена, руб.*': price,
                    'Цена до скидки, руб.': None,
                    'НДС, %*': None,
                    'Включить продвижение': None,
                    'Ozon ID': id_product,
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
                    'Объединить на одной карточке*': id_product,
                    'Цвет товара*': color_original,
                    'Российский размер*': sizes,
                    'Размер производителя': sizes_original,
                    'Статус наличия': None,
                    'Название цвета': color_original,
                    'Тип*': subcategory_name,
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

        save_excel(data=result_data, brand=brand, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, brand: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{brand}_{region}.xlsx'

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
        # get_products_urls(driver=driver, category_urls_list=category_urls_list_pl, headers=headers, region=region)
        products_urls = ["https://www.ikea.com/pl/pl/p/bymott-zaslona-2-szt-bialy-jasnoszary-w-paski-30466686/"]
        get_products_data(products_urls=products_urls, headers=headers, region=region)
    else:
        raise ValueError('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
