import os
import re
import time
from datetime import datetime

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_data_list_de
from data.data import category_data_list_tr
from data.data import category_data_list_pl
from data.data import colors_dict_de
from data.data import sizes_dict
from data.data import id_region_dict

from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

processed_urls = set()


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


# Функция получения количества страниц
def get_category_urls(driver: Chrome, region: str, id_region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/category_data_list_{region}.txt'

    category_data_list = []

    url = f"https://www2.hm.com/{id_region}/index.html"

    driver.get(url=url)
    html = driver.page_source

    soup = BeautifulSoup(html, 'lxml')

    try:
        data = soup.find('ul', class_='MLEL').find_all('li')

        for item in data:
            category_name = item.text
            try:
                category_url = f"https://www2.hm.com{item.find('a').get('href')}"
            except Exception as ex:
                print(f' category_url: {ex}')
                continue

            category_data_list.append(
                (translator(category_name), category_url)
            )

    except Exception as ex:
        print(f':get_category_urls: {ex}')

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', encoding='utf-8') as file:
        print(*category_data_list, file=file, sep='\n')


# Получаем количество страниц
def get_pages_de(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Получаем количество страниц
def get_pages_pl(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        products_total = int(soup.find('h2', class_='load-more-heading').get('data-total'))
    except Exception:
        products_total = 0

    return products_total


# Получаем количество страниц
def get_pages_tr(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Sayfalandırma'}).find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_products_urls(driver: Chrome, category_data_list: list, processed_urls: set, brand: str,
                      region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_{brand}_{region}.txt'

    count = 0

    for category_dict in category_data_list:
        for category_name, category_list in category_dict.items():
            for product_tuple in category_list:
                products_data_list = []
                products_urls = []
                subcategory_name, category_url = product_tuple

                try:
                    driver.get(url=category_url)
                    time.sleep(1)
                    html = driver.page_source
                except Exception as ex:
                    print(f"{category_url} - {ex}")
                    continue

                products_total = 0

                if region == 'Германия':
                    pages = get_pages_de(html=html)
                elif region == 'Турция':
                    pages = get_pages_tr(html=html)
                elif region == 'Польша':
                    products_total = get_pages_pl(html=html)
                else:
                    products_total = 0

                print(f'В категории {category_name}/{subcategory_name}: {products_total} товаров!')

                # for page in range(1, pages + 1):
                page_product_url = f"{category_url}?sort=stock&image-size=small&image=model&offset=0&page-size={products_total}"
                try:
                    driver.get(url=page_product_url)
                    driver.execute_script("window.scrollTo(0, 2000);")
                    time.sleep(1)
                    # driver.execute_script("window.scrollTo(0, 4000);")
                    # time.sleep(1)
                    html = driver.page_source
                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    count += 1

                    if count > 5:
                        raise ex
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('ul', {'class': 'products-listing small'}).find_all('div', class_='image-container')
                    for product_item in product_items:
                        try:
                            product_url = f"https://www2.hm.com{product_item.find('a').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {products_total} ссылок товаров!')

                if not os.path.exists(directory):
                    os.makedirs(directory)

                with open(file_path, 'a', encoding='utf-8') as file:
                    print(*products_urls, file=file, sep='\n')

                products_data_list.append(
                    {
                        (category_name, subcategory_name): products_urls
                    }
                )

                if region == 'Германия':
                    get_products_data_de(driver=driver, products_data_list=products_data_list,
                                         processed_urls=processed_urls,
                                         brand=brand, region=region)
                elif region == 'Турция':
                    get_products_data(driver=driver, products_data_list=products_data_list,
                                      processed_urls=processed_urls,
                                      brand=brand, region=region, size_model_title='Model bedeni')
                elif region == 'Польша':
                    get_products_data(driver=driver, products_data_list=products_data_list,
                                      processed_urls=processed_urls,
                                      brand=brand, region=region, size_model_title='Rozmiar modela/modelki')
                else:
                    get_products_data_de(driver=driver, products_data_list=products_data_list,
                                         processed_urls=processed_urls,
                                         brand=brand, region=region)


# Функция получения данных товаров
def get_products_data_de(driver: Chrome, products_data_list: list[dict], processed_urls: set, brand: str,
                         region: str) -> None:
    result_data = []

    count = 0

    for dict_item in products_data_list:
        product_urls = []
        key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

        for product_url in values:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                product_urls.append(product_url)
        category_name = key[0]
        subcategory_name = key[1]

        count_products = len(product_urls)
        print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')

        for i, product_url in enumerate(product_urls, 1):
            try:
                driver.get(url=product_url)
                driver.execute_script("window.scrollTo(0, 2000);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 4000);")
                time.sleep(1)
                html = driver.page_source
            except Exception as ex:
                print(f"{product_url} - {ex}")
                count += 1

                if count > 5:
                    raise ex
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                id_product = product_url.split('.')[-2]
            except Exception:
                id_product = None

            try:
                data = soup.find('div', class_='rOGz')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                name = data.find('h1').text.strip()
                product_name = f'H&M {translator(name).lower()}'
            except Exception:
                product_name = None

            try:
                price = int(''.join(
                    i for i in data.find('span', class_='edbe20 ac3d9e d9ca8b e29fbf').text.split()[0] if
                    i.isdigit())) / 100
            except Exception:
                price = None

            old_price = None

            if not price:
                try:
                    old_price = int(''.join(
                        i for i in data.find('span', class_='e98f30 ac3d9e e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    old_price = None

                try:
                    price = int(''.join(
                        i for i in data.find('span', class_='edbe20 ac3d9e c8e3aa e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    price = None

            try:
                color_original = None
                color_items = data.find('div', {'data-testid': 'grid', 'aria-live': 'polite'}).find_all('a')
                for color_item in color_items:
                    if color_item.get('aria-checked') == 'true':
                        color_original = color_item.get('title').lower()
                color_ru = colors_dict_de.get(color_original, color_original).lower()
            except Exception:
                print('not color')
                color_original = None
                color_ru = None

            try:
                images_urls_list = []
                images_items = data.find('ul', {'data-testid': 'grid-gallery'}).find_all('li')
                for item in images_items:
                    image_url = item.find('img').get('src')
                    image_url = image_url.split('?')[0]
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                print('not images')
                main_image_url = None
                additional_images_urls = None

            try:
                if category_name == 'Женщины':
                    gender = 'женский'
                elif category_name == 'Мужчины':
                    gender = 'мужской'
                else:
                    gender = category_name
            except Exception:
                gender = None

            try:
                section_description = data.find('div', id='section-descriptionAccordion')
            except Exception:
                section_description = None

            try:
                description = section_description.find('p').text.strip()
                description = translator(description)
            except Exception:
                description = None

            model_height = None
            model_size = None

            try:
                model_size_description = section_description.find('dl').find(
                    string=re.compile('Größe des Models')).find_next().text.split('cm')
            except Exception:
                model_size_description = None

            if model_size_description:
                try:
                    model_height = model_size_description[0].split()[-1]
                except Exception:
                    model_height = None

                try:
                    model_size = model_size_description[-1].split()[-1].replace('.', '').replace(')', '')
                except Exception:
                    model_size = None

            try:
                section_material_description = data.find('div', id='section-materialsAndSuppliersAccordion')
            except Exception:
                section_material_description = None

            try:
                composition_outer_shell = section_material_description.find('li').find('p').text
                composition = translator(composition_outer_shell)
                material_outer_shell = composition_outer_shell.split()[0]
                material = translator(material_outer_shell)
            except Exception:
                composition = None
                material = None

            try:
                section_care = data.find('div', id='section-careGuideAccordion').find('ul').find_all('li')
            except Exception:
                section_care = None

            try:
                care = '. '.join(i.text for i in section_care)
                care = translator(care)
            except Exception:
                care = None

            try:
                sizes_items = data.find('div', {'data-testid': 'size-selector'}).find_all('li')

                for size_item in sizes_items:
                    size_eur = size_item.find('input').get('id')
                    try:
                        size_availability = size_item.find('label').find('span').text.strip()
                    except Exception:
                        size_availability = None

                    if not size_availability:
                        status_size = 'в наличии'
                    else:
                        status_size = translator(size_availability).lower()

                    try:
                        size_rus = sizes_dict[category_name][size_eur]
                    except Exception:
                        size_rus = size_eur

                    id_product_size = f"{id_product}/{size_eur}"

                    result_data.append(
                        {
                            '№': None,
                            'Артикул': id_product_size,
                            'Название товара': product_name,
                            'Цена, руб.*': price,
                            'Цена до скидки, руб.': old_price,
                            'НДС, %*': None,
                            'Включить продвижение': None,
                            'Ozon ID': id_product_size,
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
                            'Цвет товара*': color_ru,
                            'Российский размер*': size_rus,
                            'Размер производителя': size_eur,
                            'Статус наличия': status_size,
                            'Название цвета': color_original,
                            'Тип*': subcategory_name,
                            'Пол*': gender,
                            'Размер пеленки': None,
                            'ТН ВЭД коды ЕАЭС': None,
                            'Ключевые слова': None,
                            'Сезон': None,
                            'Рост модели на фото': model_height,
                            'Параметры модели на фото': None,
                            'Размер товара на фото': model_size,
                            'Коллекция': None,
                            'Страна-изготовитель': None,
                            'Вид принта': None,
                            'Аннотация': description,
                            'Инструкция по уходу': care,
                            'Серия в одежде и обуви': None,
                            'Материал': material,
                            'Состав материала': composition,
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
            except Exception as ex:
                print(f'sizes: {product_url} - {ex}')

            print(f'Обработано: {i}/{count_products} товаров!')

        save_excel(data=result_data, species='products', brand=brand, region=region)


# Функция получения данных товаров
def get_products_data(driver: Chrome, products_data_list: list[dict], processed_urls: set, brand: str,
                      region: str, size_model_title: str) -> None:
    result_data = []

    count = 0

    for dict_item in products_data_list:
        product_urls = []
        key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

        for product_url in values:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                product_urls.append(product_url)
        category_name = key[0]
        subcategory_name = key[1]

        count_products = len(product_urls)
        print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')

        for i, product_url in enumerate(product_urls, 1):
            try:
                driver.get(url=product_url)
                driver.execute_script("window.scrollTo(0, 2000);")
                time.sleep(1)
                # driver.execute_script("window.scrollTo(0, 4000);")
                # time.sleep(1)
                html = driver.page_source
            except Exception as ex:
                print(f"{product_url} - {ex}")
                count += 1

                if count > 5:
                    raise ex
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                id_product = product_url.split('.')[-2]
            except Exception:
                id_product = None

            try:
                data = soup.find('div', class_='rOGz')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                name = data.find('h1').text.strip()
                product_name = f'H&M {translator(name).lower()}'
            except Exception:
                product_name = None

            try:
                price = int(''.join(
                    i for i in data.find('span', class_='edbe20 ac3d9e d9ca8b e29fbf').text.split()[0] if
                    i.isdigit())) / 100
            except Exception:
                price = None

            old_price = None

            if not price:
                try:
                    old_price = int(''.join(
                        i for i in data.find('span', class_='e98f30 ac3d9e e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    old_price = None

                try:
                    price = int(''.join(
                        i for i in data.find('span', class_='edbe20 ac3d9e c8e3aa e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    price = None

            try:
                color_original = data.find('div', {'data-testid': 'color-selector'}).find('p').text.strip('-').lower()
            except Exception:
                color_original = None

            try:
                images_urls_list = []
                images_items = data.find('ul', {'data-testid': 'grid-gallery'}).find_all('li')
                for item in images_items:
                    image_url = item.find('img').get('src')
                    image_url = image_url.split('?')[0]
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                print('not images')
                main_image_url = None
                additional_images_urls = None

            try:
                if category_name == 'Женщины':
                    gender = 'женский'
                elif category_name == 'Мужчины':
                    gender = 'мужской'
                else:
                    gender = category_name
            except Exception:
                gender = None

            try:
                section_description = data.find('div', id='section-descriptionAccordion')
            except Exception:
                section_description = None

            try:
                description = section_description.find('p').text.strip()
                description = translator(description)
            except Exception:
                description = None

            model_height = None
            model_size = None

            try:
                model_size_description = section_description.find('dl').find(
                    string=re.compile(size_model_title)).find_next().text.split('cm')
            except Exception:
                model_size_description = None

            if model_size_description:
                try:
                    model_height = model_size_description[0].split()[-1]
                except Exception:
                    model_height = None

                try:
                    model_size = model_size_description[-1].split()[-1].replace('.', '').replace(')', '')
                except Exception:
                    model_size = None

            try:
                section_material_description = data.find('div', id='section-materialsAndSuppliersAccordion')
            except Exception:
                section_material_description = None

            try:
                composition_outer_shell = section_material_description.find('li').find('p').text
                composition = translator(composition_outer_shell)
                material_outer_shell = composition_outer_shell.split()[0]
                material = translator(material_outer_shell)
            except Exception:
                composition = None
                material = None

            try:
                section_care = data.find('div', id='section-careGuideAccordion').find('ul').find_all('li')
            except Exception:
                section_care = None

            try:
                care = '. '.join(i.text for i in section_care)
                care = translator(care)
            except Exception:
                care = None

            try:
                sizes_items = data.find('ul', {'aria-labelledby': 'sizeSelector'}).find_all('li')
            except Exception:
                sizes_items = [' ']

            try:
                for size_item in sizes_items:
                    try:
                        size_eur = size_item.find('input').get('id')
                    except Exception:
                        size_eur = 'ONESIZE'
                    try:
                        size_availability = size_item.find('label').find('span').text.strip()
                    except Exception:
                        size_availability = None

                    if not size_availability:
                        status_size = 'в наличии'
                    else:
                        status_size = translator(size_availability).lower()

                    try:
                        size_rus = sizes_dict[category_name][size_eur]
                    except Exception:
                        size_rus = size_eur

                    id_product_size = f"{id_product}/{size_eur}"

                    result_data.append(
                        {
                            '№': None,
                            'Артикул': id_product_size,
                            'Название товара': product_name,
                            'Цена, руб.*': price,
                            'Цена до скидки, руб.': old_price,
                            'НДС, %*': None,
                            'Включить продвижение': None,
                            'Ozon ID': id_product_size,
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
                            'Российский размер*': size_rus,
                            'Размер производителя': size_eur,
                            'Статус наличия': status_size,
                            'Название цвета': color_original,
                            'Тип*': subcategory_name,
                            'Пол*': gender,
                            'Размер пеленки': None,
                            'ТН ВЭД коды ЕАЭС': None,
                            'Ключевые слова': None,
                            'Сезон': None,
                            'Рост модели на фото': model_height,
                            'Параметры модели на фото': None,
                            'Размер товара на фото': model_size,
                            'Коллекция': None,
                            'Страна-изготовитель': None,
                            'Вид принта': None,
                            'Аннотация': description,
                            'Инструкция по уходу': care,
                            'Серия в одежде и обуви': None,
                            'Материал': material,
                            'Состав материала': composition,
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
            except Exception as ex:
                print(f'sizes: {product_url} - {ex}')

            print(f'Обработано: {i}/{count_products} товаров!')

        save_excel(data=result_data, species='products', brand=brand, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str, brand: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{species}_{brand}_Аксессуары_{region}.xlsx'

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
    driver = init_chromedriver(headless_mode=True)

    brand = 'H&M'

    value = input('Введите значение:\n1 - Германия\n2 - Турция\n3 - Польша\n')
    try:
        if value == '1':
            region = 'Германия'
            base_currency = 'EUR'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс EUR/RUB: {currency}')

            get_products_urls(driver=driver, category_data_list=category_data_list_de, processed_urls=processed_urls,
                              brand=brand, region=region)
        elif value == '2':
            region = 'Турция'
            base_currency = 'TRY'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс TRY/RUB: {currency}')

            get_products_urls(driver=driver, category_data_list=category_data_list_tr, processed_urls=processed_urls,
                              brand=brand, region=region)
        elif value == '3':
            region = 'Польша'
            base_currency = 'PLN'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс PLN/RUB: {currency}')

            get_products_urls(driver=driver, category_data_list=category_data_list_pl, processed_urls=processed_urls,
                              brand=brand, region=region)

            # id_region = id_region_dict.get(region)
            # get_category_urls(driver=driver, region=region, id_region=id_region)

        else:
            raise ValueError('Введено неправильное значение')

        # # Путь к файлу для сохранения URL продуктов
        # directory = 'data'
        # file_path = f'{directory}/url_products_list_{brand}_{region}.txt'
        #
        # # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     unique_urls = set(line.strip() for line in file)
        #
        # # Сохраняем уникальные URL-адреса обратно в файл
        # with open(file_path, 'w', encoding='utf-8') as file:
        #     print(*unique_urls, file=file, sep='\n')


    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
