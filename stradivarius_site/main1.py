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
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import chunks

start_time = datetime.now()
cur_time = start_time.strftime('%d.%m.%Y %H:%M')
print(f'Дата и время сбора данных: {cur_time}')

# base_currency = 'EUR'
base_currency = 'KZT'
target_currency = 'RUB'
rub = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
# print(f'Курс EUR/RUB: {rub}')
print(f'Курс KZT/RUB: {rub}')

result_data = []


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> tuple[
    list[dict], list[dict]]:
    with open('data/id_products_list.txt', 'r', encoding='utf-8') as file:
        id_products_list = [line.strip() for line in file.readlines()]

    products_data_list = []
    new_products_data_list = []

    with Session() as session:
        for name_subcategory, id_category in id_categories_list:
            new_id_products_list = []
            try:
                time.sleep(1)
                response = session.get(
                    f'https://www.stradivarius.com/itxrest/3/catalog/store/{id_region}/category/{id_category}/product',
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
                    (name_subcategory, id_category): product_ids
                }
            )

            for id_product in product_ids:
                if str(id_product) in id_products_list:
                    continue

                new_id_products_list.append(id_product)

            if new_id_products_list:
                new_products_data_list.append(
                    {
                        (name_subcategory, id_category): new_id_products_list
                    }
                )

            print(f'Обработано: категория {name_subcategory} - {len(product_ids)} товаров!')

    new_id_products_set = set(new_id_products_list)

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
        print(*new_id_products_set, file=file, sep='\n')

    return products_data_list, new_products_data_list

# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str, species: str) -> None:
    global result_data

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
            name_subcategory = key[0]
            id_category = key[1]

            print(f'Сбор данных категории: {name_subcategory}')

            for chunk_ids in chunks(id_products_list, 300):
                id_products_str = ','.join(map(str, chunk_ids))

                params = {
                    'languageId': '-20',
                    'categoryId': id_category,
                    'productIds': id_products_str,
                    'appId': '1',
                }
                try:
                    time.sleep(1)
                    response = session.get(
                        f'https://www.stradivarius.com/itxrest/3/catalog/store/{id_region}/productsArray',
                        params=params,
                        headers=headers,
                        timeout=60
                    )

                    if response.status_code != 200:
                        print(f'status_code: {response.status_code}')
                        continue

                    json_data = response.json()

                    if species == 'size':
                        print('Сбор данных о наличии размеров!')
                        print(f'Сбор данных категории: {name_subcategory}')
                        get_size_data(products_data=json_data)
                        count += len(chunk_ids)
                        print(f'В категории {name_subcategory} обработано: {count} товаров!')
                    elif species == 'products':
                        print(f'Сбор данных категории: {name_subcategory}')
                        get_products_data(products_data=json_data, name_subcategory=name_subcategory)
                        count += len(chunk_ids)
                        print(f'В категории {name_subcategory} обработано: {count} товаров!')

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue

            if species == 'size':
                save_excel(data=result_data, species='size')

            if species == 'products':
                save_excel(data=result_data, species='products')

            result_data = []


# Функция получения данных товаров
def get_products_data(products_data: dict, name_subcategory: str) -> list[dict]:
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
            name = f"Stradivarius {item['name']}"
        except Exception:
            name = None

        if not name:
            continue

        try:
            old_price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['oldPrice']) / 100
            old_price = round(old_price * rub)
        except Exception:
            old_price = 0

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = colors_format_ru(value=color_original)
        except Exception:
            color_original = None
            color_ru = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            main_image = f"https://static.e-stradivarius.net/5/photos4/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_1_1_1.jpg"
        except Exception:
            main_image = None

        try:
            additional_images_list = []
            xmedia_data = item['bundleProductSummaries'][0]['detail']['xmedia']
            for xmedia_elem in xmedia_data:
                color_code = xmedia_elem['colorCode']
                if color_code == id_color:
                    xmedia_items = xmedia_elem['xmediaItems']
                    for xmedia_item in xmedia_items:
                        if len(additional_images_list) == 14:
                            break
                        for media_item in xmedia_item['medias']:
                            if not media_item['extraInfo']:
                                continue
                            try:
                                img_url = f"https://static.e-stradivarius.net/5/photos4/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '3_1_0.jpg' in img_url:
                                continue
                            additional_images_list.append(img_url)
                            if len(additional_images_list) == 14:
                                break

            additional_images = '; '.join(additional_images_list)
        except Exception:
            additional_images = None

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
            composition = translator(composition)
        except Exception:
            composition = None
            material = None

        brand = 'Stradivarius'
        gender = 'женский'

        try:
            size = ''
            status_dict = {}

            try:
                sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            except Exception:
                sizes_items = {}

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                if size_eur is None:
                    continue
                size_value = size_item.get('visibilityValue')
                if size == size_eur:
                    if size_value in status_dict.get(size_eur):
                        continue
                status_dict.setdefault(size_eur, []).append(size_value)
                size = size_eur

            for key, value in status_dict.items():
                size_eur = key
                if 'SHOW' in status_dict.get(key):
                    status_size = 'SHOW'
                else:
                    status_size = value[0]

                id_product_size = f"{reference}/{color_original}/{size_eur}"

                if name_subcategory == 'Обувь' or name_subcategory == 'Сумки':
                    size_rus = size_eur
                elif size_eur.isdigit():
                    size_rus = sizes_format(format='digit', size_eur=size_eur)
                elif not size_eur.isdigit():
                    size_rus = sizes_format(format='alpha', size_eur=size_eur)
                else:
                    size_rus = size_eur

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Название товара': name,
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
                        'Название цвета': color_ru,
                        'Тип*': name_subcategory,
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

    return result_data


# Функция получения данных товаров
def get_size_data(products_data: dict) -> list[dict]:
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
            name = f"Stradivarius {item['name']}"
        except Exception:
            name = None

        if not name:
            continue

        try:
            price = int(item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes'][0]['price']) / 100
            price = round(price * rub)
        except Exception:
            price = 0

        try:
            color_original = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
        except Exception:
            color_original = None

        try:
            size = ''
            status_dict = {}

            try:
                sizes_items = item['bundleProductSummaries'][0]['detail']['colors'][0]['sizes']
            except Exception:
                sizes_items = {}

            for size_item in sizes_items:
                size_eur = size_item.get('name')
                if size_eur is None:
                    continue
                size_value = size_item.get('visibilityValue')
                if size == size_eur:
                    if size_value in status_dict.get(size_eur):
                        continue
                status_dict.setdefault(size_eur, []).append(size_value)
                size = size_eur

            for key, value in status_dict.items():
                size_eur = key
                if 'SHOW' in status_dict.get(key):
                    status_size = 'SHOW'
                else:
                    status_size = value[0]

                id_product_size = f"{reference}/{color_original}/{size_eur}"

                result_data.append(
                    {
                        '№': None,
                        'Артикул': id_product_size,
                        'Цена': price,
                        'Статус наличия': status_size,
                    }
                )

        except Exception as ex:
            print(f'sizes: {ex}')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists(f'results/result_{species}_data.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_{species}_data.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_{species}_data.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_{species}_data.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_{species}_data.xlsx"')


def main():
    region = 'Казахстан'
    id_region = id_region_dict.get(region)
    if id_region is None:
        id_region = '35009503/30359534'

    print(f'Сбор данных в регионе: {region}!')

    products_data_list, products_new_data_list = get_id_products(id_categories_list=id_categories_list, headers=headers,
                                                                 params=params, id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region, species='size')

    if products_new_data_list:
        print(f'Появились  новые товары!')
        value = input('Продолжить сбор новых товаров:\n1 - Да\n2 - Нет\n')
        if value == '1':
            get_products_array(products_data_list=products_new_data_list, headers=headers, id_region=id_region,
                               species='products')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
