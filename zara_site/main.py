import os
import time
from datetime import datetime

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_categories_list_ru
from data.data import id_categories_list_baby

from data.data import id_region_dict
# from data.data import products_data_list

from functions import colors_format_ru
from functions import colors_format_en
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()

base_currency = 'EUR'
# base_currency = 'KZT'
target_currency = 'RUB'

rub = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)

print(f'Курс EUR/RUB: {rub}')
# print(f'Курс KZT/RUB: {rub}')

result_data = []


# Функция получения id категорий
def get_id_categories(headers: dict, params: dict) -> None:
    id_categories_data = []
    with Session() as session:
        try:
            response = session.get(
                'https://www.zara.com/kz/ru/categories',
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

    for category_item in category_items[:3]:
        category_name = category_item.get('sectionName')
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            subcategory_name = subcategory_item.get('name')
            subcategory_id = subcategory_item.get('id')
            redirect_category_id = subcategory_item.get('redirectCategoryId')
            category_id = redirect_category_id if redirect_category_id else subcategory_id
            id_categories_data.append((subcategory_name, category_id))
            # print(f"('{subcategory_name}', {category_id}),")
            if category_name == 'KID':
                subcategory_kid_items = subcategory_item.get('subcategories')
                for subcategory_kid_item in subcategory_kid_items:
                    subcategory_kid_name = subcategory_kid_item.get('name')
                    subcategory_kid_id = subcategory_kid_item.get('id')
                    redirect_category_kid_id = subcategory_kid_item.get('redirectCategoryId')
                    category_kid_id = redirect_category_kid_id if redirect_category_kid_id else subcategory_kid_id
                    id_categories_data.append((subcategory_kid_name, category_kid_id))

    with open('data/id_categories_list_ru.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_data, file=file, sep=',\n')


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> list[dict]:
    products_data_list = []
    id_products_set = set()
    with Session() as session:
        for category_dict in id_categories_list:
            for main_category, products_list in category_dict.items():
                for product_tuple in products_list:
                    product_ids = []
                    name_category, id_category = product_tuple

                    time.sleep(1)

                    try:
                        response = session.get(
                            f'https://www.zara.com/{id_region}/category/{id_category}/products',
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
                        product_data = json_data['productGroups']
                    except Exception:
                        product_ids = []

                    try:
                        for group_item in product_data:
                            elements = group_item['elements']
                            for element in elements:
                                try:
                                    commercial_components = element['commercialComponents']
                                except Exception:
                                    continue
                                for component in commercial_components:
                                    try:
                                        id_product = component['id']
                                    except Exception:
                                        id_product = None
                                    product_ids.append(id_product)
                                    id_products_set.add(id_product)
                    except Exception as ex:
                        print(f'id_poducts: {ex}')

                    products_data_list.append(
                        {
                            (main_category, name_category, id_category): product_ids
                        }
                    )

                    print(
                        f'Обработано: категория {main_category}/{name_category}/{id_category} - {len(product_ids)} товаров!')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
        print(*id_products_set, file=file, sep='\n')

    return products_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str) -> None:
    global result_data

    processed_ids = []

    with Session() as session:
        for dict_item in products_data_list:
            count = 0
            id_products = []
            key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

            for id_product in values:
                if id_product not in processed_ids:
                    processed_ids.append(id_product)
                    id_products.append(id_product)
            main_category = key[0]
            type_product = key[1]

            print(f'Сбор данных категории: {key[0]}/{key[1]}/{key[2]}')

            for chunk_ids in chunks(id_products, 10):
                params = {
                    'productIds': chunk_ids,
                    'ajax': 'true',
                }

                try:
                    time.sleep(1)
                    response = session.get(
                        f'https://www.zara.com/{id_region}/products-details',
                        params=params,
                        headers=headers,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')
                        continue

                    json_data = response.json()

                    if id_region == 'kz/ru':
                        result_data = get_products_data_ru(products_data=json_data, main_category=main_category,
                                                           type_product=type_product)
                    else:
                        result_data = get_products_data_en(products_data=json_data, main_category=main_category,
                                                           type_product=type_product)

                    count += len(chunk_ids)

                    print(f'В категории {key[0]}/{key[1]}/{key[2]} обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue


            save_excel(data=result_data)

            result_data = []


# Функция получения данных товаров
def get_products_data_ru(products_data: dict, main_category: str, type_product: str) -> list:
    for item in products_data:
        try:
            id_product = item['detail']['colors'][0]['productId']
        except Exception:
            id_product = None

        try:
            reference = item['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name_product = f"ZARA {item['name']}"
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_original = item['detail']['colors'][0]['name']
            color_ru = colors_format_ru(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            id_color = item['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            image_urls_list = []
            xmedia_items = item['detail']['colors'][0]['xmedia']
            for xmedia_item in xmedia_items:
                path_image = xmedia_item['path']
                name_image = xmedia_item['name']
                timestamp_image = xmedia_item['timestamp']

                try:
                    img_url = xmedia_item['url'].split('?')[0]
                except Exception:
                    img_url = f"https://static.zara.net/photos//{path_image}/w/750/{name_image}.jpg?ts={timestamp_image}"

                image_urls_list.append(img_url)

            main_image = image_urls_list[0]

            additional_images = '; '.join(image_urls_list[1:])

        except Exception:
            main_image = None
            additional_images = None


        try:
            if main_category == 'Женщины':
                gender = 'женский'
            elif main_category == 'Мужчины':
                gender = 'мужской'
            else:
                gender = main_category
        except Exception:
            gender = None

        try:
            raw_description = ' '.join(item['detail']['colors'][0]['rawDescription'].split())
            description = f"🚚 ДОСТАВКА ИЗ ЕВРОПЫ 🌍✈️<br/>✅ Регулярное обновление коллекций.<br/>✅ Полный ассортимент брендa Zara. Более 10 000 товаров ждут вас в профиле нашего магазина! 🏷️<br/>✅ Более простой поиск нужных вещей внутри нашего магазина. Подписывайтесь, чтобы всегда быть в курсе последних поступлений и акций! 🔍📲<br/>{raw_description}<br/>📣 При выборе товара ориентируйтесь на ЕВРОПЕЙСКИЙ размер!"
        except Exception:
            description = None

        brand = 'Zara'

        care = "Машинная стирка при температуре до 30ºC с коротким циклом отжима. Отбеливание запрещено. " \
               "Гладить при температуре до 110ºC. Не использовать машинную сушку. Стирать отдельно."

        if main_category == 'Женщины':
            model_height = '175'
        elif main_category == 'Мужчины':
            model_height = '180'
        else:
            model_height = None

        if main_category == 'Женщины':
            model_size = '44'
        elif main_category == 'Мужчины':
            model_size = '48'
        else:
            model_size = None

        try:
            composition_items = item['detail']['detailedComposition']['parts']

            material_outer_shell = None
            material_lining = None
            composition_outer_shell = None
            composition_lining = None

            for composition_item in composition_items:
                composition = composition_item['description']
                components_items = composition_item['components']
                if composition == 'ВНЕШНЯЯ ЧАСТЬ':
                    try:
                        material_outer_shell = components_items[0]['material']
                    except Exception:
                        material_outer_shell = None

                    try:
                        composition_outer_shell = ' '.join(
                            f"{components_item['material']}: {components_item['percentage']}" for components_item in
                            components_items)
                    except Exception:
                        composition_outer_shell = None
                elif composition == 'ПОДКЛАДКА':
                    try:
                        material_lining = components_items[0]['material']
                    except Exception:
                        material_lining = None
                    try:
                        composition_lining = ' '.join(
                            f"{components_item['material']}: {components_item['percentage']}" for components_item in
                            components_items)
                    except Exception:
                        composition_lining = None

            material = material_outer_shell if material_outer_shell else material_lining

            composition_outer_shell = composition_outer_shell if composition_outer_shell else composition_lining

        except Exception:
            material = None
            composition_outer_shell = None
            composition_lining = None

        try:
            sizes_items = item['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                status_size = size_item.get('availability')

                if main_category == 'Девочки' or main_category == 'Мальчики':
                    try:
                        size_rus = ''.join(i for i in size_eur.split()[-2] if i.isdigit())
                    except Exception:
                        size_rus = size_eur

                    if not size_rus:
                        size_rus = size_eur

                    if color_original is not None:
                        id_product_size = f"{reference}/{color_original.replace(' ', '-')}/{size_rus}"
                    else:
                        id_product_size = None

                else:
                    if size_eur.isdigit():
                        size_rus = sizes_format(format='digit', gender=main_category, size_eur=size_eur)
                    elif not size_eur.isdigit():
                        size_rus = sizes_format(format='alpha', gender=main_category, size_eur=size_eur)
                    else:
                        size_rus = size_eur

                    if color_original is not None:
                        id_product_size = f"{id_product}/{color_original.replace(' ', '-')}/{size_eur}/{reference}"
                    else:
                        id_product_size = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Название товара': name_product,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': None,
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
                        'Объединить на одной карточке*': reference,
                        'Цвет товара*': color_ru,
                        'Российский размер*': size_rus,
                        'Размер производителя': size_eur,
                        'Статус наличия': status_size,
                        'Название цвета': color_original,
                        'Тип*': type_product,
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
                        'Состав материала': composition_outer_shell,
                        'Материал подклада/внутренней отделки': composition_lining,
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

    return result_data


# Функция получения данных товаров
def get_products_data_en(products_data: dict, main_category: str, type_product: str) -> list:
    for item in products_data:
        try:
            id_product = item['detail']['colors'][0]['productId']
        except Exception:
            id_product = None

        try:
            reference = item['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name_product = item['name']
            name_product = f'ZARA {translator(name_product)}'
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_original = item['detail']['colors'][0]['name']
            color_ru = colors_format_en(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            id_color = item['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            image_urls_list = []
            xmedia_items = item['detail']['colors'][0]['xmedia']
            for xmedia_item in xmedia_items:
                path_image = xmedia_item['path']
                name_image = xmedia_item['name']
                timestamp_image = xmedia_item['timestamp']

                try:
                    img_url = xmedia_item['url'].split('?')[0]
                except Exception:
                    img_url = f"https://static.zara.net/photos//{path_image}/w/750/{name_image}.jpg?ts={timestamp_image}"

                image_urls_list.append(img_url)

            main_image = image_urls_list[0]

            additional_images = '; '.join(image_urls_list[1:])

        except Exception:
            main_image = None
            additional_images = None


        try:
            if main_category == 'Женщины':
                gender = 'женский'
            elif main_category == 'Мужчины':
                gender = 'мужской'
            else:
                gender = main_category
        except Exception:
            gender = None

        try:
            raw_description = ' '.join(item['detail']['colors'][0]['rawDescription'].split())
            raw_description = translator(raw_description)
            description = f"🚚 ДОСТАВКА ИЗ ЕВРОПЫ 🌍✈️<br/>✅ Регулярное обновление коллекций.<br/>✅ Полный ассортимент брендa Zara. Более 10 000 товаров ждут вас в профиле нашего магазина! 🏷️<br/>✅ Более простой поиск нужных вещей внутри нашего магазина. Подписывайтесь, чтобы всегда быть в курсе последних поступлений и акций! 🔍📲<br/>{raw_description}<br/>📣 При выборе товара ориентируйтесь на ЕВРОПЕЙСКИЙ размер!"
        except Exception:
            description = None

        brand = 'Zara'

        care = "Машинная стирка при температуре до 30ºC с коротким циклом отжима. Отбеливание запрещено. " \
               "Гладить при температуре до 110ºC. Не использовать машинную сушку. Стирать отдельно."

        if main_category == 'Женщины':
            model_height = '175'
        elif main_category == 'Мужчины':
            model_height = '180'
        else:
            model_height = None

        if main_category == 'Женщины':
            model_size = '44'
        elif main_category == 'Мужчины':
            model_size = '48'
        else:
            model_size = None

        try:
            composition_items = item['detail']['detailedComposition']['parts']

            material_outer_shell = None
            material_lining = None
            composition_outer_shell = None
            composition_lining = None

            for composition_item in composition_items:
                composition = composition_item['description']
                components_items = composition_item['components']
                if composition == 'OUTER SHELL':
                    try:
                        material_outer_shell = components_items[0]['material']
                        material_outer_shell = translator(material_outer_shell)
                    except Exception:
                        material_outer_shell = None

                    try:
                        composition_outer_shell = ' '.join(
                            f"{components_item['material']}: {components_item['percentage']}" for components_item in
                            components_items)
                        composition_outer_shell = translator(composition_outer_shell)
                    except Exception:
                        composition_outer_shell = None
                elif composition == 'LINING':
                    try:
                        material_lining = components_items[0]['material']
                        material_lining = translator(material_lining)
                    except Exception:
                        material_lining = None
                    try:
                        composition_lining = ' '.join(
                            f"{components_item['material']}: {components_item['percentage']}" for components_item in
                            components_items)
                        composition_lining = translator(composition_lining)
                    except Exception:
                        composition_lining = None

            material = material_outer_shell if material_outer_shell else material_lining

            composition_outer_shell = composition_outer_shell if composition_outer_shell else composition_lining

        except Exception:
            material = None
            composition_outer_shell = None
            composition_lining = None

        try:
            sizes_items = item['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                status_size = size_item.get('availability')

                if main_category == 'Девочки' or main_category == 'Мальчики' or main_category == 'Девочки;Мальчики':
                    try:
                        size_rus = ''.join(i for i in size_eur.split()[-2] if i.isdigit())
                    except Exception:
                        size_rus = size_eur

                    if not size_rus:
                        size_rus = size_eur

                    if color_original is not None:
                        id_product_size = f"{reference}/{color_original.replace(' ', '-')}/{size_rus}"
                    else:
                        id_product_size = None

                else:
                    if size_eur.isdigit():
                        size_rus = sizes_format(format='digit', gender=main_category, size_eur=size_eur)
                    elif not size_eur.isdigit():
                        size_rus = sizes_format(format='alpha', gender=main_category, size_eur=size_eur)
                    else:
                        size_rus = size_eur

                    if color_original is not None:
                        id_product_size = f"{id_product}/{color_original.replace(' ', '-')}/{size_eur}/{reference}"
                    else:
                        id_product_size = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Название товара': name_product,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': None,
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
                        'Объединить на одной карточке*': reference,
                        'Цвет товара*': color_ru,
                        'Российский размер*': size_rus,
                        'Размер производителя': size_eur,
                        'Статус наличия': status_size,
                        'Название цвета': color_original,
                        'Тип*': type_product,
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
                        'Состав материала': composition_outer_shell,
                        'Материал подклада/внутренней отделки': composition_lining,
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

    return result_data

# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/result_data_zara_en.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/result_data_zara_en.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel('results/result_data_zara_en.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter('results/result_data_zara_en.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    region = 'Германия'
    id_region = id_region_dict.get(region)
    # get_id_categories(headers=headers, params=params)
    products_data_list = get_id_products(id_categories_list=id_categories_list_ru, headers=headers, params=params,
                                         id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
