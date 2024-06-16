import os
import re
import time
from datetime import datetime

from requests import Session

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_data_list

from functions import colors_format
from functions import sizes_format
from functions import translator
from functions import get_exchange_rate
from functions import init_chromdriver

start_time = datetime.now()

rub = get_exchange_rate()

print(f'Курс EUR/RUB: {rub}')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def init_chromdriver(headless_mode=False):
    if headless_mode:
        options = Options()
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless=new")
        driver = Chrome(options=options)
        driver.implicitly_wait(15)
    else:
        driver = Chrome()
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
def get_product_urls(category_data_list: list, headers: dict, brand: str) -> list[dict]:
    url_products_set = set()

    driver = init_chromdriver(headless_mode=True)

    try:
        with Session() as session:
            for brand_dict in category_data_list:
                products_data_list = []
                category_dict = brand_dict.get(brand)
                for category_name, category_list in category_dict.items():
                    for product_tuple in category_list:
                        product_urls = []
                        subcategory_name, category_url = product_tuple

                        try:
                            time.sleep(1)
                            html = get_html(url=category_url, headers=headers, session=session)
                        except Exception as ex:
                            print(f"{category_url} - {ex}")
                            continue

                        pages = get_pages(html=html)
                        print(f'В категории {category_name}/{subcategory_name}: {pages} страниц')

                        for page in range(1, pages + 1):
                            # for page in range(1, 2):
                            page_product_url = f"{category_url}?p={page}"
                            try:
                                time.sleep(1)
                                driver.get(url=page_product_url)
                                html = driver.page_source
                            except Exception as ex:
                                print(f"{page_product_url} - {ex}")
                                continue

                            if not html:
                                continue

                            soup = BeautifulSoup(html, 'lxml')

                            # with open('data/index.html', 'w', encoding='utf-8') as file:
                            #     file.write(soup.prettify())

                            try:
                                product_items = soup.find_all('div', class_='_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6')
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

                            print(f'Обработано: {page}/{pages} страниц')

                        products_data_list.append(
                            {
                                (category_name, subcategory_name): product_urls
                            }
                        )

                        print(f'Обработано: категория {category_name}/{subcategory_name} - {len(product_urls)} товаров!')

                if not os.path.exists('data/products1'):
                    os.makedirs(f'data/products1')

                with open(f'data/products1/products_data_list_{category_name}.py', 'w', encoding='utf-8') as file:
                    print(products_data_list, file=file, sep='\n')

            with open('data/url_products_list.txt', 'a', encoding='utf-8') as file:
                print(*url_products_set, file=file, sep='\n')

        return products_data_list

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


# Функция получения данных товаров
def get_products_data(products_data_list: dict, ) -> None:
    processed_urls = []

    options = Options()

    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")

    driver = Chrome(options=options)

    try:
        for dict_item in products_data_list:
            result_data = []
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
                try:
                    time.sleep(1)
                    driver.get(product_url)
                    html = driver.page_source
                except Exception as ex:
                    print(f"{product_url} - {ex}")
                    continue

                if not html:
                    continue

                # with open('data/index_selenium.html', 'w', encoding='utf-8') as file:
                #     file.write(html)
                #
                # with open('data/index_selenium.html', 'r', encoding='utf-8') as file:
                #     html = file.read()

                soup = BeautifulSoup(html, 'lxml')

                try:
                    id_product = product_url.split('.')[-2]
                except Exception:
                    id_product = None

                try:
                    inner_data = soup.find('div', class_='inner')
                except Exception as ex:
                    print(f'inner: {product_url} - {ex}')
                    continue

                try:
                    name_product_original = inner_data.find('hm-product-name').text.strip()
                    name_product_ru = translator(name_product_original)
                    name_product = f'H&M {name_product_ru}'
                except Exception:
                    name_product = None

                try:
                    price = int(''.join(
                        i for i in inner_data.find('hm-product-price', id='product-price').text.split()[0] if
                        i.isdigit())) / 100
                    price = round(price * rub)
                except Exception:
                    price = 0

                try:
                    color_original = None
                    color_items = inner_data.find('div', class_='mini-slider').find_all('li')
                    for color_item in color_items:
                        if color_item.find('a').get('aria-checked') == 'true':
                            color_original = color_item.find('a').get('title')
                    color_ru = translator(color_original)
                except Exception:
                    color_original = None
                    color_ru = None

                try:
                    main_image = soup.find('figure',
                                           class_='pdp-image product-detail-images product-detail-main-image').find(
                        'img').get('src')
                    main_image_url = 'https:' + main_image
                except Exception:
                    main_image_url = None

                try:
                    additional_images_list = []
                    additional_images_items = soup.find_all('figure', class_='pdp-secondary-image pdp-image')

                    for additional_item in additional_images_items:
                        additional_image = additional_item.find('img').get('src')
                        additional_image_url = 'https:' + additional_image
                        additional_images_list.append(additional_image_url)
                    additional_images = '; '.join(additional_images_list)
                except Exception:
                    additional_images = []

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
                    raw_description = inner_data.find('div', class_='details parbase').find_all('div', class_='af08f4')
                except Exception:
                    raw_description = []

                try:
                    description = raw_description[0].find('p').text
                    description = translator(description)
                except Exception:
                    description = None

                model_height = None
                model_size = None

                try:
                    model_size_description = raw_description[0].find('dl').find(
                        string=re.compile('Größe des Models')).find_next().text.split('cm')
                except Exception:
                    model_height = get_model_height(category_name=category_name)
                    model_size = get_model_size(category_name=category_name)
                    model_size_description = None

                if model_size_description:
                    try:
                        model_height = model_size_description[0].split()[-1]
                    except Exception:
                        model_height = None

                    try:
                        model_size = model_size_description[-1].split()[-1].replace('.', '').replace(')', '')
                    except Exception:
                        model_size = None

                try:
                    composition_items = raw_description[1].find('ul').find_all('li')
                except Exception:
                    composition_items = []

                try:
                    composition_outer_shell = composition_items[0].find('p').text
                    composition = translator(composition_outer_shell)
                    material_outer_shell = composition_outer_shell.split()[0]
                    material = translator(material_outer_shell)
                except Exception:
                    composition = None
                    material = None

                # try:
                #     composition_lining = composition_items[1].find('p').text
                #     material_lining = composition_lining.split()[0]
                # except Exception:
                #     composition_lining = None
                #     material_lining = None

                try:
                    care = raw_description[2].find('ul').text.strip()
                    care = translator(care)
                except Exception:
                    care = None

                brand = 'H&M'

                try:
                    sizes_items = inner_data.find('hm-size-selector', class_='size-selector').find_all('li')

                    for size_item in sizes_items:
                        size_eur = size_item.find('input').get('id')

                        if size_item.find('div').get('aria-disabled') == 'true':
                            status_size = 'нет в наличии'
                        else:
                            status_size = 'в наличии'

                        if category_name == 'Женщины' or category_name == 'Мужчины':
                            if subcategory_name == 'Обувь':
                                size_rus = size_eur
                            elif size_eur.isdigit():
                                size_rus = get_sizes_format(format='digit', gender=category_name, size_eur=size_eur)
                            elif not size_eur.isdigit():
                                size_rus = get_sizes_format(format='alpha', gender=category_name, size_eur=size_eur)
                            else:
                                size_rus = size_eur
                        else:
                            if size_eur.isdigit():
                                size_rus = size_eur
                            else:
                                try:
                                    size_rus = size_eur.split()[0]
                                except Exception:
                                    size_rus = size_eur

                        id_product_size = f"{id_product}/{size_eur}"

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
                                'Ссылка на главное фото*': main_image_url,
                                'Ссылки на дополнительные фото': additional_images,
                                'Ссылки на фото 360': None,
                                'Артикул фото': None,
                                'Бренд в одежде и обуви*': brand,
                                'Объединить на одной карточке*': id_product,
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
                                'Предупреждение': None,
                            }
                        )
                except Exception as ex:
                    print(f'sizes: {product_url} - {ex}')

                print(f'Обработано: {i}/{count_products} товаров!')

            save_excel(data=result_data)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


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
    brand = 'GAP'
    # get_category_urls(url="https://en.zalando.de/mens-clothing/gap/", headers=headers)
    get_product_urls(category_data_list=category_data_list, headers=headers, brand=brand)
    # get_products_data(products_data_list=products_data_list)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
