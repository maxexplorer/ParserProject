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
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
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
        for category_dict in category_data_list:
            for category_name, category_list in category_dict.items():
                for product_tuple in category_list:
                    products_data_list = []
                    products_urls = []
                    subcategory_name, category_url = product_tuple

                    pages = 100  # Максимальное число страниц
                    last_page_with_products = 0  # Запоминаем последнюю страницу, где были товары

                    for page in range(1, pages + 1):
                        page_product_url = f"{category_url}?p={page}"
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
                            product_items = soup.find_all(
                                'div', {'data-testid': 'plp-product-grid-item'}
                            )

                            if not product_items:  # Если товаров нет, завершаем обработку категории
                                last_page_with_products = page  # Обновляем страницу, где были товары

                            for product_item in product_items:
                                try:
                                    product_url = product_item.find('a').get('href')
                                except Exception as ex:
                                    print(ex)
                                    continue
                                products_urls.append(product_url)

                        except Exception:
                            pass

                        print(f'Обработано: {page}/{pages} страниц')

                        # Проверяем кратность 10 или достижение последней страницы с товарами
                        if page % 10 == 0 or page == last_page_with_products:
                            products_data_list.append(
                                {
                                    (category_name, subcategory_name): products_urls
                                }
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
                            break

                    print(
                        f'✅ Завершена обработка {category_name}/{subcategory_name}')


# Функция получения данных товаров
def get_products_data(products_data_list: list[dict], headers: dict, processed_urls: set, brand: str,
                      region: str) -> None:
    for dict_item in products_data_list:
        result_data = []
        product_urls = []
        key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

        for product_url in values:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                product_urls.append(product_url)
        category_name = key[0]
        subcategory_name = key[1]

        count_products = len(product_urls)
        print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')

        with Session() as session:
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
                    data_json = soup.find('script', id='__NEXT_DATA__', type='application/json').text.strip()
                except Exception:
                    continue

                try:
                    # Преобразуем строку JSON в словарь
                    data_dict = json.loads(data_json)
                except json.JSONDecodeError as ex:
                    print(f'Ошибка декодирования JSON: {product_url}', ex)

                try:
                    data_items = data_dict['props']['pageProps']['dehydratedState']['queries']
                except Exception:
                    continue

                for item in data_items:
                    if 'product' in item.get('queryHash'):
                        try:
                            data = item['state']['data']
                            break
                        except Exception:
                            data = None
                if data:
                    try:
                        id_product = data['itemNumber']
                    except Exception:
                        id_product = None

                    try:
                        name = data['title']
                        product_name = f'Next {name.lower()}'
                        product_name_rus = f'Next {translator(name).lower()}'
                    except Exception:
                        product_name = None
                        product_name_rus = None

                    try:
                        colour_original = data['colour']
                        colour_rus = translator(colour_original)
                    except Exception as ex:
                        print(f'color: {product_url} - {ex}')
                        colour_original = None
                        colour_rus = None

                    try:
                        images_urls_list = []
                        images_items = data['itemMedia']
                        for item in images_items:
                            image_url = f"https://xcdn.next.co.uk{item['imageUrl']}"
                            image_url = image_url.split('?')[0]
                            images_urls_list.append(image_url)
                        main_image_url = images_urls_list[0]
                        additional_images_urls = '; '.join(images_urls_list)
                    except Exception as ex:
                        main_image_url = None
                        additional_images_urls = None

                    try:
                        item_description = data['itemDescription']
                    except Exception:
                        item_description = None

                    try:
                        sanitised_description = item_description['toneOfVoiceSanitised']
                        sanitised_description_rus = translator(sanitised_description)
                    except Exception:
                        sanitised_description = None
                        sanitised_description_rus = None

                    try:
                        logos_items = data['itemDescription']['logos']
                        logos_description = ' '.join(i['description'] for i in logos_items)
                        logos_description_rus = translator(logos_description)
                    except Exception:
                        logos_description = None
                        logos_description_rus = None

                    try:
                        measurements_items = item_description['measurements']
                        measurements_description = ' '.join(i for i in measurements_items)
                        measurements_description_rus = translator(measurements_description)
                    except Exception:
                        measurements_description = None
                        measurements_description_rus = None

                    description_original = f'{sanitised_description} {measurements_description} {logos_description}'
                    description_rus = f'{sanitised_description_rus} {measurements_description_rus} {logos_description_rus} '

                    try:
                        composition = item_description['composition']
                        composition_rus = translator(composition)
                    except Exception:
                        composition_rus = None

                    try:
                        care = item_description['washingInstructions']
                        care_rus = translator(care)
                    except Exception:
                        care_rus = None

                    try:
                        sizes_items = data['options']['options']
                    except Exception:
                        sizes_items = None

                    for size_item in sizes_items:
                        try:
                            size = size_item['name']
                        except Exception:
                            size = ''

                        try:
                            stock_status = size_item['stockStatus']
                        except Exception:
                            stock_status = None

                        try:
                            price = size_item['priceUnformatted']
                        except Exception:
                            price = None

                        result_data.append(
                            {
                                '№': product_name,
                                'Артикул': id_product,
                                'Название товара': product_name_rus,
                                'Цена, руб.*': price,
                                'Цена до скидки, руб.': None,
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
                                'Российский размер*': size,
                                'Размер производителя': size,
                                'Статус наличия': stock_status,
                                'Название цвета': colour_original,
                                'Тип*': category_name,
                                'Пол*': subcategory_name,
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
                                'Инструкция по уходу': care_rus,
                                'Серия в одежде и обуви': None,
                                'Материал': composition_rus,
                                'Состав материала': composition_rus,
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
            save_excel(data=result_data, brand=brand, category_name=category_name, region=region)


# Функция для очистки данных от некорректных символов
def clean_text(text):
    """Очистка текста от неподдерживаемых символов."""
    if isinstance(text, str):
        return text.encode('utf-8', 'ignore').decode('utf-8')  # Убираем невалидные символы
    return text


def save_excel(data: list, brand: str, category_name: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{brand}_{category_name}_{region}.xlsx'

    # Если файл не существует, создаем его с пустым DataFrame
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='ОЗОН')

    # Определяем количество уже записанных строк
    num_existing_rows = len(df.index)

    # Применяем clean_text() ко всем строковым значениям перед записью
    cleaned_data = [{k: clean_text(v) for k, v in row.items()} for row in data]

    # Преобразуем входные данные в DataFrame
    dataframe = DataFrame(cleaned_data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(
            writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
            sheet_name='ОЗОН', index=False
        )

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    brand = 'Next'

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
