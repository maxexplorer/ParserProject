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

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')


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
            if subcategory_item.get('name') == 'Clothing':
                clothing_subcategory_items = subcategory_item.get('subcategories')
                for clothing_subcategory_item in clothing_subcategory_items:
                    id_category = clothing_subcategory_item.get('id')
                    subcategory_name = clothing_subcategory_item.get('name')
                    if subcategory_name == '-':
                        continue
                    if 'Best sellers' in subcategory_name:
                        break
                    id_categories_list.append((subcategory_name, id_category))

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/data.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_list, file=file, sep='\n')

    return id_categories_list


# Функция получения id товаров
def get_id_products(id_categories_list: list, headers: dict, params: dict, id_region: str) -> list[dict]:
    products_data_list = []
    id_products_list = []
    with Session() as session:
        for name_category, id_category in id_categories_list:
            time.sleep(randint(3, 5))

            try:
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

            products_data_list.append(
                {
                    (name_category, id_category): product_ids
                }
            )

            id_products_list.extend(product_ids)

            print(f'Обработано: категория {name_category}/{id_category} - {len(product_ids)} товаров!')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/id_products_list.txt', 'a', encoding='utf-8') as file:
        print(*id_products_list, file=file, sep='\n')

    return products_data_list


# Функция получения json данных товаров
def get_products_array(products_data_list: list, headers: dict, id_region: str) -> None:
    with Session() as session:
        for dict_item in products_data_list:
            for key in dict_item:
                type_product = key[0]
                lst = dict_item[key]
                id_products = ','.join(map(str, lst))

                params = {
                    'languageId': '-1',
                    'productIds': id_products,
                    'categoryId': key[1],
                    'appId': '1',
                }

                try:
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

                    print(f'Сбор данных категории: {key[0]}/{key[1]}')
                    get_products_data(products_data=json_data, type_product=type_product)

                except Exception as ex:
                    print(f'get_products_array: {ex}')
                    continue


# Функция получения данных товаров
def get_products_data(products_data: dict, type_product: str) -> None:
    result_data = []

    for item in products_data['products']:
        try:
            id_product = item['id']
        except Exception:
            id_product = None

        try:
            reference = item['bundleProductSummaries'][0]['detail']['reference'].split('-')[0]
        except Exception:
            reference = None

        try:
            name = item['nameEn']
            name = translator(name)
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
            color_en = item['bundleProductSummaries'][0]['detail']['colors'][0]['name']
            color_ru = colors_format(value=color_en)

        except Exception:
            color_en = None
            color_ru = None

        try:
            id_color = item['bundleProductSummaries'][0]['detail']['colors'][0]['id']
        except Exception:
            id_color = ''

        try:
            main_image = f"https://static.pullandbear.net/2/photos/{item['bundleProductSummaries'][0]['detail']['colors'][0]['image']['url']}_2_1_8.jpg"
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
                                img_url = f"https://static.pullandbear.net/2/photos/{media_item['extraInfo']['url'].split('?')[0]}"
                            except Exception:
                                continue
                            if '.jpg' not in img_url or '2_1_0.jpg' in img_url or '4_1_0.jpg' in img_url or\
                                    '3_1_0.jpg' in img_url or '02/' in img_url:
                                continue
                            additional_images_list.append(img_url)
                            if len(additional_images_list) == 14:
                                break

            additional_images = '; '.join(additional_images_list)

        except Exception:
            additional_images = None

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

        brand = 'Pull&Bear'

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

            for c in sizes_items:
                size_eur = c.get('name')

                id_product_size = f"{id_product}/{color_en.replace(' ', '-')}/{size_eur}"

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
                        'Название цвета': color_en,
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

    save_excel(data=result_data)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/result_data.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/result_data.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel('results/result_data.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter('results/result_data.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    region = 'Германия'
    id_region = id_region_dict.get(region)
    if id_region is None:
        id_region = '24009400/20309422'
    # id_categories_list = get_id_categories(headers=headers, params=params, id_region=id_region)
    products_data_list = get_id_products(id_categories_list=id_category_list, headers=headers, params=params,
                                         id_region=id_region)
    get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
