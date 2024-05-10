import os
import re
import time
from datetime import datetime
from random import randint

from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_data_list
# from data.data import id_region_dict
# from functions import colors_format
# from functions import sizes_format
# from functions import translator
from functions import get_exchange_rate

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')

url = "https://www2.hm.com/de_de/index.html"

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
}


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
        pages = int(
            soup.find('div', class_='paginator').find_all('a', class_='item-page')[-1].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


# Получаем ссылки всех категорий товаров
def get_category_urls(url: str, headers: dict) -> None:
    category_data_list = []

    with Session() as session:
        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find('ul', class_='MLEL').find_all('li')

            for item in data:
                category_name = item.text
                category_url = f"https://www2.hm.com{item.find('a').get('href')}"

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
def get_product_urls(category_data_list: list, headers: dict) -> list[dict]:
    products_data_list = []
    id_products_set = set()

    with Session() as session:
        for category_dict in category_data_list:
            for category_name, category_list in category_dict.items():
                for product_tuple in category_list:
                    product_ids = []
                    subcategory_name, category_url = product_tuple

                    time.sleep(1)

                    try:
                        html = get_html(url=category_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{category_url} - {ex}")
                        continue

                    pages = get_pages(html=html)
                    print(f'В категории {category_name}: {pages} страниц')

                    for page in range(1, pages + 1):
                        page_product_url = f"{category_url}/?PAGEN_7={page}"
                        try:
                            html = get_html(url=page_product_url, headers=headers, session=session)
                        except Exception as ex:
                            print(f"{page_product_url} - {ex}")
                            continue

                        if not html:
                            continue

                        soup = BeautifulSoup(html, 'lxml')

                        try:
                            product_data = soup.find_all('div', class_='catalog-card__text-content')
                            for item in product_data:
                                try:
                                    product_url = f"https://sm-rus.ru{item.find('a', class_='card-type-and-title catalog-card__type-and-title').get('href')}"
                                    category_id = ''
                                except Exception as ex:
                                    print(ex)
                                    continue
                                product_ids.append(product_url)
                                id_products_set.add(product_url)
                        except Exception as ex:
                            print(ex)

                        products_data_list.append(
                            {
                                (category_name, subcategory_name, category_id): product_ids
                            }
                        )

                        print(f'Обработано: {page}/{pages} страниц')

                    print(f'Обработано: категория {category_name}/{subcategory_name}/{category_id} - '
                          f'{len(product_ids)} товаров!')

    if not os.path.exists('data/products'):
        os.makedirs(f'data/products')

    with open(f'data/{products_data_list}.txt', 'w', encoding='utf-8') as file:
        print(*products_data_list, file=file, sep='\n')

    return products_data_list


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
                            if '.jpg' not in img_url or '2_1_0.jpg' in img_url or '4_1_0.jpg' in img_url or \
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
    get_category_urls(url=url, headers=headers)
    # region = 'Германия'
    # id_region = id_region_dict.get(region)
    # if id_region is None:
    #     id_region = '24009400/20309422'
    # # id_categories_list = get_id_categories(headers=headers, params=params, id_region=id_region)
    # products_data_list = get_id_products(id_categories_list=id_category_list, headers=headers, params=params,
    #                                      id_region=id_region)
    # get_products_array(products_data_list=products_data_list, headers=headers, id_region=id_region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
