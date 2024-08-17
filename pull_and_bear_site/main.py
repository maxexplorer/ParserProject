import os
import time
from datetime import datetime
from random import randint

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_category_list
from data.data import id_region_dict
from functions import colors_format
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()


# Функция получения id категорий
def get_id_categories(headers: dict, params: dict, id_region: str) -> list:
    id_categories_list = []

    with Session() as session:
        try:
            response = session.get(
                f'https://www.pullandbear.com/itxrest/2/catalog/store/{id_region}/category',
                headers=headers,
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                print(f'status_code: {response.status_code}')

            json_data = response.json()
        except Exception as ex:
            print(f'get_id_categories: {ex}')

    try:
        category_items = json_data['categories']
    except Exception:
        category_items = []

    for category_item in category_items[:2]:
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            if subcategory_item.get('nameEn') == 'Clothing':
                clothing_subcategory_items = subcategory_item.get('subcategories')
                for clothing_subcategory_item in clothing_subcategory_items:
                    id_category = clothing_subcategory_item.get('id')
                    subcategory_name = clothing_subcategory_item.get('nameEn')
                    if subcategory_name == '-':
                        continue
                    if 'Best sellers' in subcategory_name:
                        break
                    id_categories_list.append((translator(subcategory_name), id_category))

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_categories_list_de.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_list, file=file, sep='\n')

    return id_categories_list


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, brand: str, region: str, id_region: str) -> \
list[dict]:
    products_data_list = []
    id_products_list = []
    with Session() as session:
        for subcategory_name, id_category in id_categories_list:
            try:
                time.sleep(randint(1, 2))
                response = session.get(
                    f'https://www.pullandbear.com/itxrest/3/catalog/store/{id_region}/category/{id_category}/product',
                    params=params,
                    headers=headers,
                    timeout=60
                )

                if response.status_code != 200:
                    print(f'id_category: {id_category} status_code: {response.status_code}')
                    continue

                json_data = response.json()

            except Exception as ex:
                print(f'get_id_products: {ex}')
                continue

            try:
                product_ids = json_data.get('productIds')
            except Exception:
                product_ids = []

            if not product_ids:
                continue

            products_data_list.append(
                {
                    (subcategory_name, id_category): product_ids
                }
            )

            id_products_list.extend(product_ids)

            print(f'Обработано: категория {subcategory_name} - {len(product_ids)} товаров!')

    id_products_set = set(id_products_list)

    if not os.path.exists('data'):
        os.makedirs('data')

    with open(f'data/id_products_list_{brand}_{region}.txt', 'a', encoding='utf-8') as file:
        print(*id_products_set, file=file, sep='\n')

    return products_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, species: str, brand: str, region: str, id_region: str,
                       currency: int) -> None:
    processed_ids = []

    with Session() as session:
        for dict_item in products_data_list:
            count = 0
            id_products_list = []
            key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

            for id_product in values:
                if id_product not in processed_ids:
                    processed_ids.append(id_product)
                    id_products_list.append(id_product)
            subcategory_name = key[0]
            id_category = key[1]

            if region == 'Германия':
                id_language = '-1'
            elif region == 'Казахстан':
                id_language = '-20'
            else:
                id_language = '-1'

            for chunk_ids in chunks(id_products_list, 300):
                id_products_str = ','.join(map(str, chunk_ids))

                params = {
                    'languageId': id_language,
                    'productIds': id_products_str,
                    'categoryId': id_category,
                    'appId': '1',
                }

                try:
                    time.sleep(randint(1, 2))
                    response = session.get(
                        f'https://www.pullandbear.com/itxrest/3/catalog/store/{id_region}/productsArray',
                        params=params,
                        headers=headers,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')
                        continue

                    json_data = response.json()

                    if region == 'Германия':
                        get_products_data_en(products_data=json_data, species=species, brand=brand, region=region,
                                             subcategory_name=subcategory_name, currency=currency)
                    elif region == 'Казахстан':
                        get_products_data_ru(products_data=json_data, species=species, brand=brand, region=region,
                                             subcategory_name=subcategory_name, currency=currency)
                    else:
                        raise 'Регион не найден!'

                    count += len(chunk_ids)

                    print(f'В категории {subcategory_name} обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue


# Функция получения данных товаров
def get_products_data_en(products_data: dict, species: str, brand: str, region: str, subcategory_name: str,
                         currency: int) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0].lstrip('0')
        except Exception:
            reference = None

        try:
            name = item['nameEn']
            product_name = f'Pull&Bear {translator(name).lower()}'
        except Exception:
            product_name = None

        if not product_name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
            old_price = round(old_price * currency)
        except Exception:
            old_price = 0

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
            price = round(price * currency)
        except Exception:
            price = 0

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name'].upper()
            color_ru = colors_format(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            main_image_url = f"https://static.pullandbear.net/2/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_1_8.jpg"
        except Exception:
            main_image_url = None

        try:
            additional_images_urls_list = []
            xmedia_data = item['bundleProductSummaries'][0]['detail']['xmedia']
            for xmedia_elem in xmedia_data:
                color_code = xmedia_elem['colorCode']
                if color_code == id_color:
                    xmedia_items = xmedia_elem['xmediaItems']
                    for xmedia_item in xmedia_items:
                        if len(additional_images_urls_list) == 14:
                            break
                        for media_item in xmedia_item['medias']:
                            if not media_item['extraInfo']:
                                continue
                            try:
                                img_url = f"https://static.pullandbear.net/2/photos/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '2_1_0.jpg' in img_url or '4_1_0.jpg' in img_url or \
                                    '3_1_0.jpg' in img_url or '02/' in img_url:
                                continue
                            additional_images_urls_list.append(img_url)
                            if len(additional_images_urls_list) == 14:
                                break

            additional_images_urls = '; '.join(additional_images_urls_list)

        except Exception:
            additional_images_urls = None

        try:
            gender_en = item['sectionNameEN']
            if gender_en == 'WOMEN':
                gender = 'женский'
            elif gender_en == 'MEN':
                gender = 'мужской'
            else:
                gender = gender_en
        except Exception:
            gender_en = None
            gender = None

        try:
            model_height = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelHeigh'].replace('cm', 'см')
        except Exception:
            model_height = None

        try:
            model_size = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelSize']
        except Exception:
            model_size = None

        try:
            description = item['detail']['longDescription']
            description = translator(description)
        except Exception:
            description = None

        try:
            care_items = item['bundleProductSummaries'][0]['detail']['care']
            care = ', '.join(item['description'] for item in care_items)
            care = translator(care)
        except Exception:
            care = None

        try:
            composition_items = item['bundleProductSummaries'][0]['detail']['composition']
            material = composition_items[0]['composition'][0]['name']
            material = translator(material)
            composition = ' '.join(
                f"{elem['name']}: {elem['percentage']}" for item in composition_items for elem in item['composition'])
            composition = translator(composition)
        except Exception:
            composition = None
            material = None

        try:
            size = ''
            status_dict = {}
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                size_value = size_item.get('visibilityValue')

                if size == size_eur:
                    if size_value in status_dict.get(size_eur):
                        continue
                status_dict.setdefault(size_eur, []).append(size_value)
                size = size_eur

            for size_item in sizes_items:
                size_eur = size_item.get('name')

                if size == size_eur:
                    continue
                size = size_eur

                if 'SHOW' in status_dict.get(size_eur):
                    status_size = 'SHOW'
                else:
                    status_size = status_dict.get(size_eur)[0]

                if size_eur.isdigit() and gender_en:
                    size_rus = sizes_format(format='digit', gender=gender_en, size_eur=size_eur)
                elif not size_eur.isdigit() and gender_en:
                    size_rus = sizes_format(format='alpha', gender=gender_en, size_eur=size_eur)
                else:
                    size_rus = size_eur.replace('-', ';')

                id_product_size = f"{reference}/{id_color}/{size_eur}"

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
                        'Объединить на одной карточке*': reference,
                        'Цвет товара*': color_ru,
                        'Код цвета': id_color,
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
            print(f'sizes: {ex}')

    save_excel(data=result_data, species=species, brand=brand, region=region)


# Функция получения данных товаров
def get_products_data_ru(products_data: dict, species: str, brand: str, region: str, subcategory_name: str,
                         currency: int) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0].lstrip('0')
        except Exception:
            reference = None

        try:
            name = item['name']
            product_name = f'Pull&Bear {name.lower()}'
        except Exception:
            product_name = None

        if not product_name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
            old_price = round(old_price * currency)
        except Exception:
            old_price = 0

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
            price = round(price * currency)
        except Exception:
            price = 0

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = color_original
        except Exception:
            color_original = None
            color_ru = None

        try:
            main_image_url = f"https://static.pullandbear.net/2/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_1_8.jpg"
        except Exception:
            main_image_url = None

        try:
            additional_images_urls_list = []
            xmedia_data = item['bundleProductSummaries'][0]['detail']['xmedia']
            for xmedia_elem in xmedia_data:
                color_code = xmedia_elem['colorCode']
                if color_code == id_color:
                    xmedia_items = xmedia_elem['xmediaItems']
                    for xmedia_item in xmedia_items:
                        if len(additional_images_urls_list) == 14:
                            break
                        for media_item in xmedia_item['medias']:
                            if not media_item['extraInfo']:
                                continue
                            try:
                                img_url = f"https://static.pullandbear.net/2/photos/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '2_1_0.jpg' in img_url or '4_1_0.jpg' in img_url or \
                                    '3_1_0.jpg' in img_url or '02/' in img_url:
                                continue
                            additional_images_urls_list.append(img_url)
                            if len(additional_images_urls_list) == 14:
                                break

            additional_images_urls = '; '.join(additional_images_urls_list)

        except Exception:
            additional_images_urls = None

        try:
            gender_en = item['sectionNameEN']
            if gender_en == 'WOMEN':
                gender = 'женский'
            elif gender_en == 'MEN':
                gender = 'мужской'
            else:
                gender = gender_en
        except Exception:
            gender_en = None
            gender = None

        try:
            model_height = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelHeigh'].replace('cm', 'см')
        except Exception:
            model_height = None

        try:
            model_size = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelSize']
        except Exception:
            model_size = None

        try:
            description = item['detail']['longDescription']
            description = translator(description)
        except Exception:
            description = None

        try:
            care_items = item['bundleProductSummaries'][0]['detail']['care']
            care = ', '.join(item['description'] for item in care_items)
        except Exception:
            care = None

        try:
            composition_items = item['bundleProductSummaries'][0]['detail']['composition']
            material = composition_items[0]['composition'][0]['name']
            composition = ' '.join(
                f"{elem['name']}: {elem['percentage']}" for item in composition_items for elem in item['composition'])
        except Exception:
            composition = None
            material = None

        try:
            size = ''
            status_dict = {}
            sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                size_value = size_item.get('visibilityValue')

                if size == size_eur:
                    if size_value in status_dict.get(size_eur):
                        continue
                status_dict.setdefault(size_eur, []).append(size_value)
                size = size_eur

            for size_item in sizes_items:
                size_eur = size_item.get('name')

                if size == size_eur:
                    continue
                size = size_eur

                if 'SHOW' in status_dict.get(size_eur):
                    status_size = 'SHOW'
                else:
                    status_size = status_dict.get(size_eur)[0]

                if size_eur.isdigit():
                    size_rus = sizes_format(format='digit', gender=gender_en, size_eur=size_eur)
                elif not size_eur.isdigit() and gender_en:
                    size_rus = sizes_format(format='alpha', gender=gender_en, size_eur=size_eur)
                else:
                    size_rus = size_eur.replace('-', ';')

                id_product_size = f"{reference}/{id_color}/{size_eur}"

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
                        'Объединить на одной карточке*': reference,
                        'Цвет товара*': color_ru,
                        'Код цвета': id_color,
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
            print(f'sizes: {ex}')

    save_excel(data=result_data, species=species, brand=brand, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str, brand: str, region: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists(f'results/result_data_{species}_{brand}_{region}.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_data_{species}_{brand}_{region}.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_data_{species}_{brand}_{region}.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_data_{species}_{brand}_{region}.xlsx', mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    brand = 'Pull&Bear'

    # region = 'Германия'
    # id_region = id_region_dict.get(region)
    # id_categories_list = get_id_categories(headers=headers, params=params, id_region=id_region)

    value = input('Введите значение:\n1 - Германия\n2 - Казахстан\n')
    if value == '1':
        region = 'Германия'
        base_currency = 'EUR'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс EUR/RUB: {currency}')
    elif value == '2':
        region = 'Казахстан'
        base_currency = 'KZT'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс KZT/RUB: {currency}')
    else:
        raise ValueError('Введено неправильное значение')

    id_region = id_region_dict.get(region)

    products_data_list = get_id_products(id_categories_list=id_category_list, headers=headers, params=params,
                                         brand=brand, region=region, id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, species='products', brand=brand,
                       region=region, id_region=id_region, currency=currency)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
