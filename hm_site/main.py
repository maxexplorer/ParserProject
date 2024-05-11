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
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
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
                for product_tuple in category_list[:1]:
                    product_urls = []
                    subcategory_name, category_url = product_tuple

                    time.sleep(1)

                    try:
                        html = get_html(url=category_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{category_url} - {ex}")
                        continue

                    pages = get_pages(html=html)
                    print(f'В категории {category_name}: {pages} страниц')

                    # for page in range(1, pages + 1):
                    for page in range(1, 2):
                        page_product_url = f"{category_url}?page={page}"
                        try:
                            html = get_html(url=page_product_url, headers=headers, session=session)
                        except Exception as ex:
                            print(f"{page_product_url} - {ex}")
                            continue

                        if not html:
                            continue

                        soup = BeautifulSoup(html, 'lxml')

                        try:
                            product_items = soup.find('div',
                                                      id='products-listing-section').find_next().find_next_sibling()
                            for product_item in product_items:
                                try:
                                    product_url = product_item.find('a').get('href')
                                except Exception as ex:
                                    print(ex)
                                    continue
                                product_urls.append(product_url)
                                id_products_set.add(product_url)
                        except Exception as ex:
                            print(ex)

                        products_data_list.append(
                            {
                                (category_name, subcategory_name): product_urls
                            }
                        )

                        print(f'Обработано: {page}/{pages} страниц')

                    print(f'Обработано: категория {category_name}/{subcategory_name} - {len(product_urls)} товаров!')

    if not os.path.exists('data'):
        os.makedirs(f'data')

    with open(f'data/products_data_list.py', 'w', encoding='utf-8') as file:
        print(products_data_list, file=file, sep='\n')

    return products_data_list


# Функция получения данных товаров
def get_products_data(products_data_list: dict, type_product: str) -> None:
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

            print(f'Сбор данных категории: {category_name}/{subcategory_name}')

            for i, product_url in enumerate(product_urls, 1):
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
                    id_product = product_url.split('.')[-2]
                except Exception:
                    id_product = None

                try:
                    reference = ''
                except Exception:
                    reference = None

                try:
                    name_product = f"H&M {}"
                except Exception:
                    name_product = None

                try:
                    price = 0
                    price = round(price * rub)
                except Exception:
                    price = 0

                try:
                    color_original = ''
                    color_ru = colors_format_ru(value=color_original)
                except Exception:
                    color_original = None
                    color_ru = None

                try:
                    id_color = ''
                except Exception:
                    id_color = ''

                try:
                    image_urls_list = []
                    main_image = ''
                    additional_images = []
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
                    raw_description = ''
                    description = f"🚚 ДОСТАВКА ИЗ ЕВРОПЫ 🌍✈️<br/>✅ Регулярное обновление коллекций.<br/>✅ Полный ассортимент брендa Zara. Более 10 000 товаров ждут вас в профиле нашего магазина! 🏷️<br/>✅ Более простой поиск нужных вещей внутри нашего магазина. Подписывайтесь, чтобы всегда быть в курсе последних поступлений и акций! 🔍📲<br/>{raw_description}<br/>📣 При выборе товара ориентируйтесь на ЕВРОПЕЙСКИЙ размер!"
                except Exception:
                    description = None

                brand = 'Zara'

                care = "Машинная стирка при температуре до 30ºC с коротким циклом отжима. Отбеливание запрещено. " \
                       "Гладить при температуре до 110ºC. Не использовать машинную сушку. Стирать отдельно."

                if category_name == 'Женщины':
                    model_height = '175'
                elif category_name == 'Мужчины':
                    model_height = '180'
                else:
                    model_height = None

                if category_name == 'Женщины':
                    model_size = '44'
                elif category_name == 'Мужчины':
                    model_size = '48'
                else:
                    model_size = None

                try:
                    composition = ''
                    material = ''
                except Exception:
                    material = None
                    composition = None

                try:
                    sizes_items = []

                    for size_item in sizes_items:
                        size_eur = size_item.get('name')


                        if category_name == 'Девочки' or category_name == 'Мальчики':
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
    # get_category_urls(url=url, headers=headers)
    get_product_urls(category_data_list=category_data_list, headers=headers)
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
