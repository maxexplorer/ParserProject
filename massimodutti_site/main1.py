import os
import time
from datetime import datetime

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_category_list
from data.data import id_region_dict
from functions import colors_format_ru
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, brand: str, region: str,
                    id_region: str) -> tuple[list[dict], list[dict]]:
    products_data_list = []
    products_new_data_list = []
    new_id_set = set()

    directory = 'data'

    # Путь к файлу для сохранения идентификаторов продуктов
    file_path = f'{directory}/id_products_list_{brand}_{region}.txt'

    with open(file_path, 'r', encoding='utf-8') as file:
        id_products_list = [line.strip() for line in file.readlines()]

    with Session() as session:
        for category_dict in id_categories_list:
            for category_name, products_list in category_dict.items():
                for product_tuple in products_list:
                    subcategory_name, id_category = product_tuple

                    new_id_list = []

                    try:
                        time.sleep(1)
                        response = session.get(
                            f'https://www.massimodutti.com/itxrest/3/catalog/store/{id_region}/category/{id_category}/product',
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

                    products_data_list.append(
                        {
                            (category_name, subcategory_name): product_ids
                        }
                    )

                    for id_product in product_ids:
                        if str(id_product) in id_products_list:
                            continue

                        new_id_list.append(id_product)
                        id_products_list.append(id_product)
                        new_id_set.add(id_product)

                    if new_id_list:
                        products_new_data_list.append(
                            {
                                (category_name, subcategory_name): product_ids
                            }
                        )

                    print(f'Обработано: категория {category_name}/{subcategory_name} - {len(product_ids)} товаров!')

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'a', encoding='utf-8') as file:
        print(*new_id_set, file=file, sep='\n')

    return products_data_list, products_new_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, species: str, brand: str, region: str, id_region: str) -> None:
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
            category_name = key[0]
            subcategory_name = key[1]

            print(f'Сбор данных категории: {category_name}/{subcategory_name}')

            if region == 'Германия' or region == 'Турция' or region == 'Польша':
                id_language = '-1'
            elif region == 'Казахстан':
                id_language = '-20'
            else:
                id_language = '-1'

            for chunk_ids in chunks(id_products_list, 300):
                id_products_str = ','.join(map(str, chunk_ids))

                params = {
                    'languageId': id_language,
                    'appId': '1',
                    'productIds': id_products_str,
                }

                try:
                    time.sleep(1)
                    response = session.get(
                        f'https://www.massimodutti.com/itxrest/3/catalog/store/{id_region}/productsArray',
                        params=params,
                        headers=headers,
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')
                        continue

                    json_data = response.json()

                    if species == 'size':
                        print(f'Сбор данных о наличии размеров категории: {subcategory_name}')
                        get_size_data(products_data=json_data, species=species, brand=brand, region=region)
                    elif species == 'products' and (region == 'Германия' or region == 'Турция' or region == 'Польша'):
                        get_products_data_en(products_data=json_data, species=species, brand=brand, region=region,
                                             category_name=category_name, subcategory_name=subcategory_name)
                    elif species == 'products' and region == 'Казахстан':
                        get_products_data_ru(products_data=json_data, species=species, brand=brand, region=region,
                                             category_name=category_name, subcategory_name=subcategory_name)
                    else:
                        raise 'Регион не найден!'

                    count += len(chunk_ids)

                    print(f'В категории {category_name}/{subcategory_name} обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue


# Функция получения данных товаров
def get_products_data_en(products_data: dict, species: str, brand: str, region: str, category_name: str,
                         subcategory_name: str) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['displayReference']
        except Exception:
            reference = None

        try:
            name = item['name']
            product_name = f"Massimo Dutti {translator(name.lower())}"
        except Exception:
            product_name = None

        if not product_name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
        except Exception:
            old_price = None

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        except Exception:
            price = None

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = colors_format_ru(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = None

        try:
            main_image_url = f"https://static.massimodutti.net/3/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_5_16.jpg"
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
                                img_url = f"https://static.massimodutti.net/3/photos/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '3_1_0.jpg' in img_url:
                                continue
                            additional_images_urls_list.append(img_url)
                            if len(additional_images_urls_list) == 14:
                                break

            additional_images_urls = '; '.join(additional_images_urls_list)
        except Exception:
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
            model_height = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelHeigh'].replace('cm', 'см')
        except Exception:
            model_height = None

        try:
            model_size = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelSize']
        except Exception:
            model_size = None

        try:
            attributes = item['attributes']
            description = '. '.join(attr['value'] for attr in attributes)
            description = translator(description.replace('BASESTYLE. ', ''))
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
            try:
                sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            except Exception:
                sizes_items = {}

            for size_item in sizes_items:
                try:
                    size_eur = size_item.get('name')
                except Exception:
                    size_eur = ''
                try:
                    status_size = size_item.get('visibilityValue')
                except Exception:
                    status_size = ''

                if size_eur.isdigit():
                    size_rus = sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                elif not size_eur.isdigit():
                    size_rus = sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
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
def get_products_data_ru(products_data: dict, species: str, brand: str, region: str, category_name: str,
                         subcategory_name: str) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['displayReference']
        except Exception:
            reference = None

        try:
            name = item['name']
            product_name = f"Massimo Dutti {name.lower()}"
        except Exception:
            product_name = None

        if not product_name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
        except Exception:
            old_price = None

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        except Exception:
            price = None

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = colors_format_ru(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = None

        try:
            main_image_url = f"https://static.massimodutti.net/3/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_5_16.jpg"
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
                                img_url = f"https://static.massimodutti.net/3/photos/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '3_1_0.jpg' in img_url:
                                continue
                            additional_images_urls_list.append(img_url)
                            if len(additional_images_urls_list) == 14:
                                break

            additional_images_urls = '; '.join(additional_images_urls_list)
        except Exception:
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
            model_height = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelHeigh'].replace('cm', 'см')
        except Exception:
            model_height = None

        try:
            model_size = item['bundleProductSummaries'][0]['detail']['colors'][0]['modelSize']
        except Exception:
            model_size = None

        try:
            attributes = item['attributes']
            description = '. '.join(attr['value'] for attr in attributes)
            description = description.replace('BASESTYLE. ', '')
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
            try:
                sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            except Exception:
                sizes_items = {}

            for size_item in sizes_items:
                try:
                    size_eur = size_item.get('name')
                except Exception:
                    size_eur = ''
                try:
                    status_size = size_item.get('visibilityValue')
                except Exception:
                    status_size = ''

                if not size_eur:
                    id_product_size = reference
                else:
                    id_product_size = f"{reference}/{id_color}/{size_eur}"

                if size_eur.isdigit():
                    size_rus = sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                elif not size_eur.isdigit():
                    size_rus = sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
                else:
                    size_rus = size_eur.replace('-', ';')

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
def get_size_data(products_data: dict, species: str, brand: str, region: str) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            reference = item['bundleProductSummaries'][0]['detail']['displayReference']
        except Exception:
            reference = None

        try:
            name = item['name']
            product_name = f"Massimo Dutti {translator(name.lower())}"
        except Exception:
            product_name = None

        if not product_name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
        except Exception:
            old_price = None

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
        except Exception:
            price = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = None

        try:
            try:
                sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            except Exception:
                sizes_items = {}

            for size_item in sizes_items:
                try:
                    size_eur = size_item.get('name')
                except Exception:
                    size_eur = ''
                try:
                    status_size = size_item.get('visibilityValue')
                except Exception:
                    status_size = ''

                id_product_size = f"{reference}/{id_color}/{size_eur}"

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Цена': price,
                        'Цена до скидки, руб.': old_price,
                        'Статус наличия': status_size,
                    }
                )

        except Exception as ex:
            print(f'sizes: {ex}')

    save_excel(data=result_data, species=species, brand=brand, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str, brand: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{species}_{brand}_{region}.xlsx'

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

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    brand = 'MassimoDutti'

    value = input('Введите значение:\n1 - Германия\n2 - Казахстан\n3 - Турция\n4 - Польша\n')
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
    elif value == '3':
        region = 'Турция'
        base_currency = 'TRY'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс TRY/RUB: {currency}')
    elif value == '4':
        region = 'Польша'
        base_currency = 'PLN'
        target_currency = 'RUB'
        currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
        print(f'Курс PLN/RUB: {currency}')
    else:
        raise ValueError('Введено неправильное значение')

    id_region = id_region_dict.get(region)

    products_data_list, products_new_data_list = get_id_products(id_categories_list=id_category_list, headers=headers,
                                                                 params=params, brand=brand, region=region,
                                                                 id_region=id_region)
    print('Сбор данных о наличии размеров!')
    get_products_array(products_data_list=products_data_list, headers=headers, species='size', brand=brand,
                       region=region, id_region=id_region)
    if products_new_data_list:
        print(f'Появились  новые товары!')
        value = input('Продолжить сбор новых товаров:\n1 - Да\n2 - Нет\n')
        if value == '1':
            get_products_array(products_data_list=products_new_data_list, headers=headers, species='products', brand=brand,
                               region=region, id_region=id_region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
