import json
import os
import re
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

from data.data import category_urls_list_cookware_pl
from data.data import category_urls_list_textile_tr
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
def get_products_urls(driver: Chrome, category_urls_list: list, headers: dict, brand: str, category: str,
                      region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_{brand}_{category}_{region}.txt'

    with Session() as session:
        for category_url in category_urls_list:
            products_urls = set()

            print(f'Обрабатывается категория: {category_url}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            if region == 'Польша':
                pages = get_pages(html=html)
            elif region == 'Турция':
                pages = 20

            for page in range(1, pages + 1):
                category_page_url = f"{category_url}?page={page}"
                try:
                    driver.get(url=category_page_url)
                    driver.execute_script("window.scrollTo(0, 2000);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, 4000);")
                    time.sleep(1)
                    html = driver.page_source
                except Exception as ex:
                    print(f"{category_page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    # product_items = soup.find('div', class_='plp-product-list__products').find_all('div',
                    #                                                                                class_='plp-fragment-wrapper')

                    product_items = soup.find_all('div', class_='product-item-text')

                    if not product_items:
                        break

                    for product_item in product_items:
                        try:
                            product_url = f"https://www.ikea.com.tr{product_item.find('a').get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.add(product_url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, 'a', encoding='utf-8') as file:
                print(*products_urls, file=file, sep='\n')

            # get_products_data_tr(products_urls=products_urls, headers=headers, brand=brand, category=category, region=region)
            #
            # print(f'Обработано: {category_url}')


# Функция получения данных товаров
def get_products_data_pl(products_urls: list, headers: dict, brand: str, category: str, region: str) -> None:
    result_data = []
    batch_size = 100

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
                product_information_json = data.find('div',
                                                     class_="pip-product__subgrid product-pip js-product-pip").get(
                    'data-hydration-props')

                product_information_dict = json.loads(product_information_json)
            except Exception:
                continue

            try:
                id_product = product_information_dict['buyModule']['productNumber']
            except Exception:
                id_product = None

            try:
                product_name_original = product_information_dict['pipPriceModule']['productName'].capitalize()
                product_description_original = product_information_dict['pipPriceModule']['productDescription']
                product_name_ru = translator(product_name_original)
                product_name = f'IKEA {product_name_original} {product_name_ru} {translator(product_description_original).lower()}'
            except Exception:
                product_name = None

            try:
                price = product_information_dict['pipPriceModule']['price']['mainPriceProps']['price']['integer']
            except Exception:
                price = None

            try:
                color_original = product_information_dict['productStylePicker']['variationStyles'][0]['selectedOption']
                color = translator(color_original)
            except Exception:
                color_original = None
                color = None

            try:
                images_urls_list = []
                product_gallery = product_information_dict['productGallery']['mediaList']
                for item_gallery in product_gallery:
                    image_url = item_gallery['content']['url']
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                product_details_props = product_information_dict['productInformationSection']['productDetailsProps']
                try:
                    paragraphs = ' '.join(
                        paragraph for paragraph in product_details_props['productDescriptionProps']['paragraphs'])
                except Exception:
                    paragraphs = None
                try:
                    designer_label = product_details_props['productDescriptionProps']['designerLabel']
                except Exception:
                    designer_label = None
                try:
                    designer_name = product_details_props['productDescriptionProps']['designerName']
                except Exception:
                    designer_name = None

                description_original = f'{paragraphs} {designer_label} {designer_name}'
                description = translator(description_original)

                try:
                    materials_and_care = product_details_props['accordionObject']['materialsAndCare']['contentProps']
                    try:
                        materials_original = ' '.join(
                            material_info['material'] for material_group in materials_and_care['materials'] for
                            material_info in material_group['materials'])
                        materials = translator(materials_original)
                        material_items = materials.split()
                        material = material_items[1].rstrip(',')
                        if material == '%':
                            material = material_items[2].rstrip(',')
                    except Exception:
                        materials = None
                        material = None
                    try:
                        care_original = ' '.join(
                            care_info for care_group in materials_and_care['careInstructions'] for
                            care_info in care_group['texts'])
                        care = translator(care_original)
                    except Exception:
                        care = None

                except Exception:
                    pass
            except Exception:
                description = None

            try:
                dimension_props = product_information_dict['productInformationSection']['dimensionProps']

                try:
                    product_dimensions_original = ', '.join(
                        f"{item['name']}: {item['measure']}" for item in dimension_props['dimensions'])
                    product_dimensions = translator(product_dimensions_original)
                except Exception:
                    product_dimensions = None

                try:
                    packaging_items = dimension_props['packaging']['contentProps']['packages'][0]['measurements'][0]
                    packaging_dict = {item['type']: item['text'] for item in packaging_items}

                    try:
                        pack_width = int(packaging_dict['width'].split()[0]) * 10
                    except Exception:
                        pack_width = None
                    try:
                        pack_height = int(packaging_dict['height'].split()[0]) * 10
                    except Exception:
                        pack_height = None
                    try:
                        pack_length = int(packaging_dict['length'].split()[0]) * 10
                    except Exception:
                        pack_length = None
                    try:
                        pack_weight = float(packaging_dict['weight'].split()[0]) * 1000
                    except Exception:
                        pack_weight = None
                except Exception:
                    pass
            except Exception:
                pass

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
                    'Вес в упаковке, г*': pack_weight,
                    'Ширина упаковки, мм*': pack_width,
                    'Высота упаковки, мм*': pack_height,
                    'Длина упаковки, мм*': pack_length,
                    'Ссылка на главное фото*': main_image_url,
                    'Ссылки на дополнительные фото': additional_images_urls,
                    'Ссылки на фото 360': None,
                    'Артикул фото': None,
                    'Бренд в одежде и обуви*': brand,
                    'Объединить на одной карточке*': id_product,
                    'Цвет товара*': color,
                    'Российский размер*': product_dimensions,
                    'Размер производителя': product_dimensions_original,
                    'Статус наличия': None,
                    'Название цвета': color_original,
                    'Тип*': category,
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
                    'Инструкция по уходу': care,
                    'Серия в одежде и обуви': None,
                    'Материал': material,
                    'Состав материала': materials,
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

            # Записываем данные в Excel каждые 100 URL
            if len(result_data) >= batch_size:
                save_excel(data=result_data, brand=brand, category=category, region=region)
                result_data.clear()  # Очищаем список для следующей партии

        # Записываем оставшиеся данные в Excel
        if result_data:
            save_excel(data=result_data, brand=brand, category=category, region=region)


# Функция получения данных товаров
def get_products_data_tr(products_urls: list, headers: dict, brand: str, category: str, region: str) -> None:
    result_data = []
    batch_size = 100

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
                item_list_element = soup.find_all('li', {'itemprop': 'itemListElement'})
            except Exception:
                item_list_element = None

            try:
                subcategory = item_list_element[-2].text.strip().capitalize()
            except Exception:
                subcategory = None

            try:
                product_name_original = f'IKEA {item_list_element[-1].text.strip().capitalize()}'
            except Exception:
                product_name_original = None

            try:
                product_name_rus = translator(product_name_original)
            except Exception:
                product_name_rus = None

            data = soup.find('div', class_='product-detail-wrapper')

            try:
                id_product = data.find('div', class_='product-code').text.strip()
            except Exception:
                id_product = None

            try:
                price = ''.join(filter(lambda x: x.isdigit(), data.find('span', class_='price-box').text.strip()))
            except Exception:
                price = None

            try:
                color_original = data.find('span', class_='product-color-name').text.strip()
            except Exception:
                color_original = None
            try:
                color_rus = translator(color_original)
            except Exception:
                color_rus = None

            try:
                product_dimensions = soup.find('span', string=re.compile('Ölçü')).find_next().text.strip()
            except Exception:
                product_dimensions = None

            try:
                images_urls_list = []
                product_gallery = data.find('div', class_='product-detail-img').find_all('li')
                for item_gallery in product_gallery:
                    image_url = item_gallery.find('img').get('src')
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                main_image_url = None
                additional_images_urls = None

            try:
                description_original = ''.join(
                    item.text.strip() for item in data.find('div', class_='product-description').find_all('p'))
            except Exception:
                description_original = None

            try:
                description_rus = translator(description_original)
            except Exception:
                description_rus = None

            try:
                materials_original = soup.find('h4', string=re.compile('Malzeme')).find_next().text.strip()
                materials_rus = translator(materials_original)
            except Exception:
                materials_rus = None

            try:
                material_original = materials_original.split()[1].rstrip(',')
                material_rus = translator(material_original)
            except Exception:
                material_rus = None

            try:
                care_original = soup.find('h3', string=re.compile('Bakım Talimatları')).find_next().text.strip()
                care_rus = translator(care_original)
            except Exception:
                care_rus = None

            try:
                package_dimensions = soup.find('h3', string=re.compile('Paket Ölçüleri')).find_next()
            except Exception:
                package_dimensions = None

            try:
                pack_width = int(''.join(filter(lambda x: x.isdigit(), package_dimensions.find('p', string=re.compile(
                    'Genişlik')).text.strip().split(':')[1]))) * 10
            except Exception:
                pack_width = None
            try:
                pack_height = int(''.join(filter(lambda x: x.isdigit(), package_dimensions.find('p', string=re.compile(
                    'Yükseklik')).text.strip().split(':')[1]))) * 10
            except Exception:
                pack_height = None
            try:
                pack_length =  int(''.join(filter(lambda x: x.isdigit(), package_dimensions.find('p', string=re.compile(
                    'Uzunluk')).text.strip().split(':')[1]))) * 10
            except Exception:
                pack_length = None

            try:
                pack_weight_gross_text = package_dimensions.find('p', string=re.compile(
                    'Toplam ağırlık')).text.strip()
                if 'kg' in pack_weight_gross_text:
                    pack_weight = int(float(pack_weight_gross_text.split(':')[1].split()[0]) * 1000)
                else:
                    pack_weight = int(pack_weight_gross_text.split(':')[1].split()[0])
            except Exception:
                pack_weight = None

            if not pack_weight:
                try:
                    pack_weight_text = package_dimensions.find('p', string=re.compile('Ağırlık')).text.strip()
                    if 'kg' in pack_weight_text:
                        pack_weight = int(float(pack_weight_text.split(':')[1].split()[0]) * 1000)
                    else:
                        pack_weight = int(pack_weight_text.split(':')[1].split()[0])

                except Exception:
                    pack_weight = None


            result_data.append(
                {
                    '№': product_name_original,
                    'Артикул': id_product,
                    'Название товара': product_name_rus,
                    'Цена, руб.*': price,
                    'Цена до скидки, руб.': None,
                    'НДС, %*': None,
                    'Включить продвижение': None,
                    'Ozon ID': id_product,
                    'Штрихкод (Серийный номер / EAN)': None,
                    'Вес в упаковке, г*': pack_weight,
                    'Ширина упаковки, мм*': pack_width,
                    'Высота упаковки, мм*': pack_height,
                    'Длина упаковки, мм*': pack_length,
                    'Ссылка на главное фото*': main_image_url,
                    'Ссылки на дополнительные фото': additional_images_urls,
                    'Ссылки на фото 360': None,
                    'Артикул фото': None,
                    'Бренд в одежде и обуви*': brand,
                    'Объединить на одной карточке*': id_product,
                    'Цвет товара*': color_rus,
                    'Российский размер*': product_dimensions,
                    'Размер производителя': product_dimensions,
                    'Статус наличия': None,
                    'Название цвета': color_original,
                    'Тип*': subcategory,
                    'Пол*': 'Tekstil',
                    'Размер пеленки': None,
                    'ТН ВЭД коды ЕАЭС': None,
                    'Ключевые слова': None,
                    'Сезон': None,
                    'Рост модели на фото': None,
                    'Параметры модели на фото': None,
                    'Размер товара на фото': None,
                    'Коллекция': None,
                    'Страна-изготовитель': None,
                    'Вид принта': description_original,
                    'Аннотация': description_rus,
                    'Инструкция по уходу': care_rus,
                    'Серия в одежде и обуви': None,
                    'Материал': material_rus,
                    'Состав материала': materials_rus,
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

            # Записываем данные в Excel каждые 100 URL
            if len(result_data) >= batch_size:
                save_excel(data=result_data, brand=brand, category=category, region=region)
                result_data.clear()  # Очищаем список для следующей партии

        # Записываем оставшиеся данные в Excel
        if result_data:
            save_excel(data=result_data, brand=brand, category=category, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, brand: str, category: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{brand}_{category}_{region}.xlsx'

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
    brand = 'IKEA'
    category = 'Tekstil'

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
    else:
        raise ValueError('Введено неправильное значение')
    #
    # get_products_urls(driver=driver, category_urls_list=category_urls_list_textile_tr, headers=headers, brand=brand,
    #                   category=category, region=region)
    directory = 'data'
    file_path = f'{directory}/url_products_list_{brand}_{category}_{region}.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        products_urls = [line.strip() for line in file.readlines()]

    get_products_data_tr(products_urls=products_urls, headers=headers, brand=brand, category=category, region=region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
