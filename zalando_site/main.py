import os
import re
import time
from datetime import datetime
import json

from requests import Session

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

# from data.data import category_data_list
# from data.data import brand_dict

from functions import colors_format
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}


def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
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
        print(ex)


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('span', {'aria-live': 'polite'}).text.strip().split()[-1])
    except Exception as ex:
        print(f'get_pages: {ex}')
        pages = 1

    return pages


# Получаем ссылки всех категорий товаров
def get_category_urls(url: str, headers: dict) -> None:
    category_data_list = []

    with Session() as session:
        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find('ul', class_='ODGSbs').find_all('li')

            for item in data:
                category_name = item.text
                category_name = translator(category_name)
                try:
                    category_url = item.find('a').get('href')
                except Exception as ex:
                    print(ex)
                    continue

                category_data_list.append(
                    (category_name, category_url)
                )

        except Exception as ex:
            print(ex)

        if not os.path.exists('data'):
            os.makedirs('data')

        with open(f'data/category_data_list.txt', 'w', encoding='utf-8') as file:
            print(*category_data_list, file=file, sep='\n')


# Получаем ссылки товаров
def get_product_urls(category_data_list: list, headers: dict, brand: str, driver: Chrome) -> None:
    url_products_set = set()

    with Session() as session:
        for brand_dict in category_data_list:
            category_dict = brand_dict.get(brand)
            if category_dict is None:
                continue
            for category_name, category_list in category_dict.items():
                for product_tuple in category_list:
                    products_data_list = []
                    product_urls = []
                    subcategory_name, category_url = product_tuple

                    try:
                        html = get_html(url=category_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{category_url} - {ex}")
                        continue

                    pages = get_pages(html=html)
                    print(f'В категории {category_name}/{subcategory_name}: {pages} страниц')

                    for page in range(1, pages + 1):
                        page_product_url = f"{category_url}?p={page}"
                        try:
                            driver.get(url=page_product_url)
                            time.sleep(1)
                            driver.execute_script("window.scrollTo(0, 4000);")
                            html = driver.page_source
                        except Exception as ex:
                            print(f"{page_product_url} - {ex}")
                            continue

                        if not html:
                            continue

                        soup = BeautifulSoup(html, 'lxml')

                        try:
                            product_items = soup.find_all('div',
                                                          class_='_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6')
                            for product_item in product_items:
                                try:
                                    product_url = product_item.find('a').get('href')
                                except Exception as ex:
                                    print(ex)
                                    continue
                                product_urls.append(product_url)
                                url_products_set.add(product_url)
                        except Exception as ex:
                            print(ex)

                        print(f'Обработано: {page}/{pages} страниц!')

                    products_data_list.append(
                        {
                            (category_name, subcategory_name): product_urls
                        }
                    )

                    print(f'Обработано: категория {category_name}/{subcategory_name} - {len(product_urls)} товаров!')

                    # if not os.path.exists('data'):
                    #     os.makedirs(f'data')
                    #
                    # with open(f'data/products_data_list_{category_name}.py', 'w', encoding='utf-8') as file:
                    #     print(products_data_list, file=file, sep='\n')

                    get_products_data(products_data_list=products_data_list, brand=brand)

                    with open(f'data/url_products_list_{brand}.txt', 'a', encoding='utf-8') as file:
                        print(*url_products_set, file=file, sep='\n')


# Функция получения данных товаров
def get_products_data(products_data_list: list[dict], brand: str) -> None:
    result_data = []
    processed_urls = []

    with Session() as session:
        for dict_item in products_data_list:
            product_urls = []
            key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

            for product_url in values:
                if product_url not in processed_urls:
                    processed_urls.append(product_url)
                    product_urls.append(product_url)
            category_name = key[0]
            subcategory_name = key[1]

            count_products = len(product_urls)

            print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')
            for i, product_url in enumerate(product_urls, 1):
                image_urls_list = []
                try:
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{product_url} - {ex}")
                    continue

                if not html:
                    continue

                try:
                    # Регулярное выражение для извлечения текста
                    pattern = r'{"cache".*'

                    # Найти совпадение в тексте
                    match = re.search(pattern, html)

                    if match:
                        extracted_text = match.group(0).rstrip(');')
                        # print(extracted_text)
                        try:
                            # Преобразуем строку JSON в словарь
                            data_dict = json.loads(extracted_text)
                        except json.JSONDecodeError as ex:
                            print("Ошибка декодирования JSON:", ex)
                    else:
                        print("Совпадение не найдено")
                        continue
                except Exception as ex:
                    print(f'regular expression: {ex}')

                try:
                    data_dict = data_dict['cache']
                except Exception as ex:
                    print(f'data_dict: {ex}')
                    continue

                if category_name == 'Женщины':
                    gender = 'женский'
                elif category_name == 'Мужчины':
                    gender = 'мужской'
                else:
                    gender = category_name

                for key_product in data_dict:
                    # Обработка product_items
                    try:
                        product_data = data_dict[key_product]['data']['product']
                        media_items = product_data['media']
                    except Exception:
                        continue

                    try:
                        for media_item in media_items:
                            image_url = media_item['uri'].split('?')[0]
                            if image_url not in image_urls_list:
                                image_urls_list.append(image_url)
                        main_image = image_urls_list[0]
                        additional_images = '; '.join(image_urls_list[1:])
                    except Exception:
                        continue
                    try:
                        name_product = product_data['name']
                        name_product = translator(name_product)
                    except Exception:
                        name_product = ''
                    try:
                        sku = product_data['sku']
                    except Exception:
                        sku = ''
                    # try:
                    #     brand = product_data['brand']['name']
                    # except Exception:
                    #     brand = ''
                    try:
                        color_data = product_data['color']
                    except Exception:
                        color_data = {}
                    try:
                        color_name = color_data['name']
                    except Exception:
                        color_name = ''
                    try:
                        color_label = color_data['label']
                        color_ru = translator(color_label)
                    except Exception:
                        color_ru = ''

                    if len(additional_images) > 1 and name_product and sku and color_name:
                        break

                composition = ''
                material = ''
                care = ''
                description1 = ''
                description2 = ''

                for key_attribute in data_dict:
                    # Обработка detail_items
                    try:
                        attribute_items = data_dict[key_attribute]['data']['product']['attributeSuperClusters']
                    except Exception:
                        continue
                    if not name_product or not sku:
                        try:
                            product_data = data_dict[key_attribute]['data']['product']
                        except Exception:
                            pass
                        try:
                            name_product = product_data['name']
                            name_product = translator(name_product)
                        except Exception:
                            name_product = ''
                        try:
                            sku = product_data['sku']
                        except Exception:
                            sku = ''

                    for attribute_item in attribute_items:
                        try:
                            if attribute_item['id'] == 'material_care':
                                clusters = attribute_item['clusters']
                                for cluster in clusters:
                                    attributes = cluster['attributes']
                                    for attribute in attributes:
                                        if attribute['key'] == 'Outer fabric material':
                                            composition = attribute['value']
                                            composition = translator(composition)
                                            material_items = composition.split()
                                            material = material_items[1].rstrip(',')
                                            if material == '%':
                                                material = material_items[2].rstrip(',')
                                            material = translator(material)
                                        if attribute['key'] == 'Care instructions':
                                            care = attribute['value']
                                            care = translator(care)
                        except Exception:
                            composition = ''
                            material = ''
                            care = ''

                        try:
                            if attribute_item['id'] == 'details':
                                clusters = attribute_item['clusters']
                                for cluster in clusters:
                                    attributes = cluster['attributes']
                                    description1 = '<br/> <br/>'.join(
                                        f"{attribute['key']}: {attribute['value']}" for attribute in attributes if
                                        attribute['key'] != 'Article number')
                                    description1 = translator(description1)
                        except Exception:
                            description1 = ''
                        try:
                            if attribute_item['id'] == 'size_fit':
                                clusters = attribute_item['clusters']
                                for cluste in clusters:
                                    attributes = cluste['attributes']
                                    description2 = '<br/> <br/>'.join(
                                        f"{attribute['key']}: {attribute['value']}" for attribute in attributes)
                                    description2 = translator(description2)
                        except Exception:
                            description2 = ''

                description = f"{description1} '<br/> <br/>' {description2}"

                for key_size in data_dict:
                    # Обработка size_items
                    try:
                        context_data = data_dict[key_size]['data']['context']
                        size_items = context_data['simples']
                    except Exception:
                        continue
                    if not color_name:
                        try:
                            color_name = context_data['color']['name']
                        except Exception:
                            color_name = ''
                        color_ru = color_name

                    for size_item in size_items:
                        try:
                            size_eur = size_item['size']
                        except Exception:
                            size_eur = ''
                        try:
                            status_size = size_item['offer']['stock']['quantity']
                        except Exception:
                            status_size = ''
                        try:
                            price_data = size_item['offer']['price']
                        except Exception:
                            price_data = {}
                        try:
                            price_original = int(price_data['original']['amount']) / 100
                            price_original = round(price_original * rub)
                        except Exception:
                            price_original = ''
                        try:
                            price_discount = (price_data['promotional']['amount']) / 100
                            price_discount = round(price_discount * rub)
                        except Exception:
                            price_discount = ''

                        if category_name == 'Девочки;Мальчики':
                            size_rus = size_eur
                        elif subcategory_name == 'Обувь':
                            size_rus = size_eur
                        elif size_eur.isdigit():
                            size_rus = sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                        elif not size_eur.isdigit():
                            size_rus = sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
                        else:
                            size_rus = size_eur

                        id_product_size = f"{sku}/{size_eur}/{color_name}"

                        result_data.append(
                            {
                                '№': None,
                                'Артикул': id_product_size,
                                'Название товара': name_product,
                                'Цена, руб.*': price_discount,
                                'Цена до скидки, руб.': price_original,
                                'НДС, %*': None,
                                'Включить продвижение': None,
                                'Ozon ID': id_product_size,
                                'Штрихкод (Серийный номер / EAN)': None,
                                'Вес в упаковке, г*': None,
                                'Ширина упаковки, мм*': None,
                                'Высота упаковки, мм*': None,
                                'Длина упаковки, мм*': None,
                                'Ссылка на главное фото*': main_image,
                                'Ссылки на дополнительные фото': additional_images,
                                'Ссылки на фото 360': None,
                                'Артикул фото': None,
                                'Бренд в одежде и обуви*': brand,
                                'Объединить на одной карточке*': sku,
                                'Цвет товара*': color_ru,
                                'Российский размер*': size_rus,
                                'Размер производителя': size_eur,
                                'Статус наличия': status_size,
                                'Название цвета': color_name,
                                'Тип*': subcategory_name,
                                'Пол*': gender,
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
                                'Состав материала': composition,
                                # 'Материал подклада/внутренней отделки': None,
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
                                'Предупреждение': None
                            }
                        )

                print(f'Обработано: {i}/{count_products} товаров!')

        save_excel(data=result_data, brand=brand, species='products')


# Функция для записи данных в формат xlsx
def save_excel(data: list, brand: str, species: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists(f'results/result_data_{species}_{brand}.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_data_{species}_{brand}.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_data_{species}_{brand}.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_data_{species}_{brand}.xlsx', mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    # get_category_urls(url="https://en.zalando.de/kids-clothing/columbia/", headers=headers)
    try:
        value = input(
            'Введите значение:\n1 - Tommy Hilfiger\n2 - Jack & Jones\n3 - Pepe Jeans\n4 - Calvin Klein\n'
            '5 - Scotch & Soda\n6 - GAP\n7 - Helly Hansen\n8 - The North Face\n9 - Tom Tailor\n10 - s.Oliver\n11 - G-Star\n'
            '12 - Esprit\n13 - Guess\n14 - Mango\n15 - Adidas\n16 - Nike\n17 - Puma\n18 - Vans\n19 - ASICS\n20 - Under Armour\n'
            '21 - Reebok\n22 - Columbia\n')
        brand = brand_dict.get(value)
    except KeyError:
        raise 'Такой бренд отсутствует в словаре!'

    print(f'Сбор данных бренда: {brand}')

    if brand:
        try:
            driver = init_chromedriver(headless_mode=True)
        except Exception as ex:
            raise f'driver: {ex}'
        try:
            get_product_urls(category_data_list=category_data_list, headers=headers, brand=brand, driver=driver)
        except Exception as ex:
            print(f'main: {ex}')
        finally:
            driver.close()
            driver.quit()
    else:
        print('Введено некорректное значение!')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
