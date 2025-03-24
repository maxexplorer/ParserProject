import os
import time
from datetime import datetime
import json

from requests import Session

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_data_list_tr

from functions import translator
from functions import get_exchange_rate
from functions import get_unique_urls

start_time = datetime.now()

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            raise Exception(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('div', class_='pagination').find_all('a')[-3].text.strip())
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_category_urls(url: str) -> None:
    try:
        session = Session()
        html = get_html(url=url, headers=headers, session=session)
    except Exception as ex:
        print(f'get_category_urls: {ex}')
        raise 'not html'
    soup = BeautifulSoup(html, 'lxml')

    category_items = soup.find('nav', id='main-menu').find_all('li', class_='w-100')

    for i, elem in enumerate(category_items, 1):
        print(f"('{elem.text.strip()}', '{elem.find('a').get('href')}'),")


# Функция получения ссылок товаров
def get_products_urls(category_data_list: list, headers: dict, brand: str, region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_{brand}_{region}.txt'

    try:
        processed_urls = get_unique_urls(file_path=file_path)
    except FileNotFoundError:
        processed_urls = set()

    with Session() as session:
        for category_name, category_url in category_data_list:
            products_data_list = []
            products_urls = []

            print(f'Обрабатывается категория: {category_url}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                page_product_url = f"{category_url}?pg={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=page_product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_product_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('div', {'class': 'col-12', 'data-selector': '.product-detail-card'
                                                      }).find_all('a', class_='col-12 product-title')
                    for product_item in product_items:
                        try:
                            product_url = f"https://www.kozmela.com{product_item.get('href')}"
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)
                except Exception:
                    pass

                print(f'Обработано: {page}/{pages} страниц')

                # Проверяем кратность 10 или достижение последней страницы с товарами
                if page % 10 == 0 or page == pages:
                    products_data_list.append(
                        (
                            category_name, products_urls
                        )
                    )

                    get_products_data(products_data_list=products_data_list,
                                      headers=headers,
                                      processed_urls=processed_urls,
                                      brand=brand, region=region)

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    with open(file_path, 'a', encoding='utf-8') as file:
                        print(*products_urls, file=file, sep='\n')

                    products_urls.clear()  # Очищаем список после обработки
                    products_data_list.clear()  # Очищаем накопленные данные

            print(f'✅ Завершена обработка {category_name}')


# Функция получения данных товаров
def get_products_data(products_data_list: list[tuple], headers: dict, processed_urls: set, brand: str,
                      region: str) -> None:
    for category_name, product_urls in products_data_list:
        result_data = []
        unique_product_urls = []
        for product_url in product_urls:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                unique_product_urls.append(product_url)
        count_products = len(unique_product_urls)
        print(f'В категории {category_name}: {count_products} товаров!')

        with Session() as session:
            for i, product_url in enumerate(unique_product_urls, 1):
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
                    data = soup.find('div', id='product-detail')
                except Exception:
                    continue

                try:
                    name = data.find('h1', class_='product-title').text.strip()
                    product_name = f'{brand} {name.lower()}'
                    product_name_rus = f'{brand} {translator(name).lower()}'
                except Exception:
                    product_name = None
                    product_name_rus = None

                try:
                    id_product = data.find('div', class_='barcode-code').find('span', id='supplier-barcode-code'
                                                                              ).text.strip()
                except Exception:
                    id_product = None

                try:
                    price_not_discounted = data.find('span', class_='product-price-not-discounted').text.strip()
                except Exception:
                    price_not_discounted = None

                try:
                    price = data.find('div', class_='product-current-price fw-black').find('span',
                                                                                           class_='product-price').text.strip()
                except Exception:
                    price = None

                colour_original = None
                colour_rus = None

                try:
                    images_urls_list = []
                    images_items = soup.find_all('a', class_='swiper-slide product-images-item')
                    for item in images_items:
                        image_url = item.get('href')
                        images_urls_list.append(image_url)
                    main_image_url = images_urls_list[0]
                    additional_images_urls = '; '.join(images_urls_list)
                except Exception:
                    main_image_url = None
                    additional_images_urls = None

                try:
                    description_original = data.find('div', id='product-fullbody').text.strip()
                except Exception:
                    description_original = None

                try:
                    description_rus = translator(description_original)
                except Exception:
                    description_rus = None

                result_data.append(
                    {
                        '№': product_name,
                        'Артикул': id_product,
                        'Название товара': product_name_rus,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': price_not_discounted,
                        'НДС, %*': None,
                        'Включить продвижение': None,
                        'Ozon ID': id_product,
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
                        'Объединить на одной карточке*': id_product,
                        'Цвет товара*': colour_rus,
                        'Российский размер*': None,
                        'Размер производителя': None,
                        'Статус наличия': None,
                        'Название цвета': colour_original,
                        'Тип*': category_name,
                        'Пол*': None,
                        'Размер пеленки': None,
                        'ТН ВЭД коды ЕАЭС': None,
                        'Ключевые слова': None,
                        'Сезон': None,
                        'Рост модели на фото': None,
                        'Параметры модели на фото': None,
                        'Размер товара на фото': None,
                        'Коллекция': None,
                        'Страна-изготовитель': None,
                        'Вид принта': description_original,
                        'Аннотация': description_rus,
                        'Инструкция по уходу': None,
                        'Серия в одежде и обуви': None,
                        'Материал': None,
                        'Состав материала': None,
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

                print(f'Обработано: {i}/{count_products} товаров!')

            if result_data:
                save_excel(data=result_data, brand=brand, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, brand: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{brand}_{region}.xlsx'

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

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    brand = 'Kozmela'

    region = 'Турция'
    base_currency = 'TRY'
    target_currency = 'RUB'
    currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
    print(f'Курс TRY/RUB: {currency}')

    get_products_urls(category_data_list=category_data_list_tr, headers=headers, brand=brand, region=region)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
