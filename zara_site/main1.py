import os
import time
from datetime import datetime

from requests import Session

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from configs.config import headers
from configs.config import params
from data.data import id_categories_list

from data.data import id_region_dict

from functions import colors_format_ru
from functions import colors_format_en
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()

result_data = []


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> tuple[
    list[dict], list[dict]]:
    region = id_region.split('/')[0]

    products_data_list = []
    products_new_data_list = []

    with Session() as session:
        for category_dict in id_categories_list:
            for category_name, products_list in category_dict.items():
                for product_tuple in products_list:
                    with open(f'data/id_products_list_Zara_{region}.txt', 'r', encoding='utf-8') as file:
                        id_products_list = [line.strip() for line in file.readlines()]
                    product_ids = []
                    new_id_list = []
                    subcategory_name, id_category = product_tuple

                    if id_region == 'kz/ru' and category_name == 'Девочки;Мальчики':
                        continue

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

                    if not product_data:
                        continue

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

                                    if str(id_product) in id_products_list:
                                        continue
                                    new_id_list.append(id_product)

                    except Exception as ex:
                        print(f'id_poducts: {ex}')

                    products_data_list.append(
                        {
                            (category_name, id_category): product_ids
                        }
                    )

                    if new_id_list:
                        products_new_data_list.append(
                            {
                                (category_name, id_category): new_id_list
                            }
                        )

                    print(
                        f'Обработано: категория {category_name}/{subcategory_name} - {len(product_ids)} товаров!')

                    if not os.path.exists('data'):
                        os.makedirs('data')

                    with open(f'data/id_products_list_Zara_{region}.txt', 'a', encoding='utf-8') as file:
                        print(*new_id_list, file=file, sep='\n')

    return products_data_list, products_new_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str, species: str, currency: int) -> None:
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
            category_name = key[0]
            subcategory_name = key[1]

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

                    if species == 'size':
                        print(f'Сбор данных категории: {category_name}/{subcategory_name}')
                        get_size_data(products_data=json_data, id_region=id_region, currency=currency)
                    elif species == 'products' and id_region == 'kz/ru':
                        print(f'Сбор данных категории: {category_name}/{subcategory_name}')
                        get_products_data_ru(products_data=json_data, category_name=category_name,
                                             subcategory_name=subcategory_name, currency=currency)
                    elif species == 'products' and id_region == 'de/en':
                        print(f'Сбор данных категории: {category_name}/{subcategory_name}')
                        get_products_data_en(products_data=json_data, category_name=category_name,
                                             subcategory_name=subcategory_name, currency=currency)
                    count += len(chunk_ids)

                    print(f'Обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue

            region = id_region.split('/')[0]

            save_excel(data=result_data, species=species, region=region)

            result_data = []


# Функция получения данных товаров
def get_products_data_ru(products_data: dict, category_name: str, subcategory_name: str, currency: int) -> None:
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
            name_product = f"Zara {item['name'].lower()}"
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            old_price = int(item['detail']['colors'][0]['oldPrice']) / 100
            old_price = round(old_price * currency)
        except Exception:
            old_price = 0

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * currency)
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
            if category_name == 'Женщины':
                gender = 'женский'
            elif category_name == 'Мужчины':
                gender = 'мужской'
            else:
                gender = category_name
        except Exception:
            gender = None

        try:
            raw_description = ' '.join(item['detail']['colors'][0]['rawDescription'].split())
            description = raw_description
        except Exception:
            description = None

        brand = 'Zara'

        care = "Машинная стирка при температуре до 30ºC с коротким циклом отжима. Отбеливание запрещено. " \
               "Гладить при температуре до 110ºC. Не использовать машинную сушку. Стирать отдельно."

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

                if category_name == 'Девочки' or category_name == 'Мальчики':
                    size_rus = ''.join(i for i in size_eur.split()[-2] if i.isdigit())
                elif subcategory_name == 'Обувь' or subcategory_name == 'Аксессуары' or subcategory_name == 'Сумка':
                    size_rus = size_eur
                elif size_eur.isdigit():
                    size_rus = sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                elif not size_eur.isdigit():
                    size_rus = sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
                else:
                    size_rus = size_eur

                if color_original is not None:
                    id_product_size = f"{reference}/{id_color}/{size_eur}"
                else:
                    id_product_size = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Название товара': name_product,
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


# Функция получения данных товаров
def get_products_data_en(products_data: dict, category_name: str, subcategory_name: str, currency: int) -> None:
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
            name_product = f'Zara {translator(name_product).lower()}'
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            old_price = int(item['detail']['colors'][0]['oldPrice']) / 100
            old_price = round(old_price * currency)
        except Exception:
            old_price = 0

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * currency)
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
            if category_name == 'Женщины':
                gender = 'женский'
            elif category_name == 'Мужчины':
                gender = 'мужской'
            else:
                gender = category_name
        except Exception:
            gender = None

        try:
            raw_description = ' '.join(item['detail']['colors'][0]['rawDescription'].split())
            description = translator(raw_description)
        except Exception:
            description = None

        brand = 'Zara'

        care = "Машинная стирка при температуре до 30ºC с коротким циклом отжима. Отбеливание запрещено. " \
               "Гладить при температуре до 110ºC. Не использовать машинную сушку. Стирать отдельно."

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

                if category_name == 'Девочки' or category_name == 'Мальчики' or category_name == 'Девочки;Мальчики':
                    size_rus = ''.join(i for i in size_eur.split()[-2] if i.isdigit())
                elif subcategory_name == 'Обувь' or subcategory_name == 'Аксессуары' or subcategory_name == 'Сумка':
                    size_rus = size_eur
                elif size_eur.isdigit():
                    size_rus = sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                elif not size_eur.isdigit():
                    size_rus = sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
                else:
                    size_rus = size_eur

                if color_original is not None:
                    id_product_size = f"{reference}/{id_color}/{size_eur}"
                else:
                    id_product_size = None

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Название товара': name_product,
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


# Функция получения данных о размерах товаров
def get_size_data(products_data: dict, id_region: str, currency: int) -> list[dict]:
    for item in products_data:
        try:
            reference = item['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name_product = item['name'].lower()
            if id_region == 'de/en':
                name_product = f'Zara {translator(name_product)}'
            else:
                name_product = f'Zara {name_product}'
        except Exception:
            name_product = None

        if not name_product:
            continue

        try:
            old_price = int(item['detail']['colors'][0]['oldPrice']) / 100
            old_price = round(old_price * currency)
        except Exception:
            old_price = 0

        try:
            price = int(item['detail']['colors'][0]['price']) / 100
            price = round(price * currency)
        except Exception:
            price = 0

        try:
            id_color = item['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            sizes_items = item['detail']['colors'][0]['sizes']

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                status_size = size_item.get('availability')

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


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str, region: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists(f'results/result_data_{species}_Zara_{region}.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_data_{species}_Zara_{region}.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_data_{species}_Zara_{region}.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_data_{species}_Zara_{region}.xlsx', mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
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
    products_data_list, products_new_data_list = get_id_products(id_categories_list=id_categories_list, headers=headers,
                                                                 params=params, id_region=id_region)
    print('Сбор данных о наличии размеров!')
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region, species='size',
                       currency=currency)

    if products_new_data_list:
        print(f'Появились  новые товары!')
        value = input('Продолжить сбор новых товаров:\n1 - Да\n2 - Нет\n')
        if value == '1':
            get_products_array(products_data_list=products_new_data_list, headers=headers, id_region=id_region,
                               species='products', currency=currency)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
