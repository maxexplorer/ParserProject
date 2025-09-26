import os
import time
from datetime import datetime
import json

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

# Засекаем время запуска программы
start_time = datetime.now()

# Заголовки HTTP-запросов (имитация браузера)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}

category_dict = {
    "https://shop.uralaz.ru/catalog/dvigatel/",
    "https://shop.uralaz.ru/catalog/transmissiya/",
    "https://shop.uralaz.ru/catalog/khodovaya-chast/",
    "https://shop.uralaz.ru/catalog/rulevoe-upravlenie/",
    "https://shop.uralaz.ru/catalog/tormoznaya-sistema/",
    "https://shop.uralaz.ru/catalog/elektro-oborudovanie/",
    "https://shop.uralaz.ru/catalog/instrument-i-prinadlezhnosti/",
    "https://shop.uralaz.ru/catalog/kabina-i-operenie/",
    "https://shop.uralaz.ru/catalog/platforma-i-kuzov/",
    "https://shop.uralaz.ru/catalog/normali/",
    "https://shop.uralaz.ru/catalog/podshipniki/",
    "https://shop.uralaz.ru/catalog/remni-rti/",
}


def get_html(url: str, headers: dict, session: Session) -> str | None:
    """
    Выполняет GET-запрос по указанному URL и возвращает HTML-код страницы.

    :param url: Ссылка на страницу
    :param headers: Заголовки запроса (user-agent и др.)
    :param session: Сессия requests для повторного использования соединений
    :return: HTML содержимое страницы или None в случае ошибки
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')
        return None


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML.

    :param html: HTML код страницы
    :return: Количество страниц (если не найдено — возвращает 55 по умолчанию)
    """
    soup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу пагинации
        page_url = soup.find('div', class_='pages').find('li', class_='last').find('a').get('href')
        match = re.search(r"page=(\d+)", page_url)
        return int(match.group(1)) if match else 1
    except Exception:
        return 1


def get_products_urls(url: str, headers: dict) -> list[dict]:
    """
    Собирает ссылки на товары по категориям.

    :param url: Ссылка на страницу каталога
    :param headers: Заголовки запроса
    :return: Список словарей {имя_категории: [список ссылок на товары]}
    """
    product_data_list = []

    # Создаем requests.Session для ускорения запросов
    with Session() as session:
        try:
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f'get_products_urls: {ex}')
            return product_data_list

        soup = BeautifulSoup(html, 'lxml')

        # Получаем список категорий
        try:
            data = soup.find_all('li', class_='menu-item-catalog')
        except Exception as ex:
            print(f'data: {ex}')
            data = []

        # Перебираем категории
        for item in data:
            product_urls = []
            try:
                category_name = item.find('a', itemprop='url').text.strip()
            except Exception:
                category_name = None

            try:
                product_items = item.find('ul', class_='sub-menu').find_all('a')
            except Exception:
                continue

            # Перебираем товары внутри категории
            for i, product_item in enumerate(product_items, 1):
                try:
                    product_url = product_item.get('href')
                except Exception:
                    continue

                product_urls.append(product_url)
                print(f'Получена ссылка: {i}')

            product_data_list.append({category_name: product_urls})
            print(f'Обработана категория: {category_name}')

    # Сохраняем список ссылок в JSON
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/product_data_list.json', 'a', encoding='utf-8') as file:
        json.dump(product_data_list, file, indent=4, ensure_ascii=False)

    return product_data_list




def save_excel(data: list[dict], category_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data_{category_name}.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Export Products Sheet', index=False)

    df_existing = read_excel(file_path, sheet_name='Export Products Sheet')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Export Products Sheet', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')



def get_products_data(file_path: str) -> list[dict]:
    """
    Извлекает данные о товарах (название, описание, характеристики, фото и т.д.)
    по ссылкам из сохранённого JSON-файла.

    :param file_path: Путь к JSON-файлу с категориями и ссылками на товары
    :return: Список словарей с данными о каждом товаре
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        product_data_list = json.load(file)

    result_data = []

    # Создаем requests.Session для ускорения
    with Session() as session:
        for category_dict in product_data_list:
            for category_name, product_urls in category_dict.items():
                for product_url in product_urls:
                    try:
                        time.sleep(1)  # пауза между запросами
                        html = get_html(url=product_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{product_url} - {ex}")
                        continue

                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'lxml')

                    # Название товара
                    try:
                        title = soup.find('h1').text.strip()
                    except Exception:
                        title = None

                    # Блок с описанием
                    try:
                        content_data = soup.find('div', class_='entry-content')
                    except Exception as ex:
                        print(f'content_data: {product_url} - {ex}')
                        continue

                    # Текстовое описание
                    try:
                        description = ''.join(i.text.strip().replace('\xa0', ' ') for i in content_data.find_all('p'))
                    except Exception:
                        description = ''

                    # Характеристики (таблица)
                    try:
                        characteristic = ''
                        characteristic_items = content_data.find('table').find_all('tr')
                        for characteristic_item in characteristic_items:
                            characteristic += '\n' + ' '.join(
                                c.text.strip().replace('\xa0', ' ') for c in characteristic_item.find_all('td'))
                    except Exception:
                        characteristic = ''

                    description = f'{description}\n{characteristic}'

                    # Изображения
                    try:
                        images_urls_list = []
                        images_items = content_data.find_all('figure', class_='gallery-item')
                        for image_item in images_items:
                            image_url = f"{image_item.find('a').get('href')}"
                            images_urls_list.append(image_url)
                        images_urls = ', '.join(images_urls_list)
                    except Exception:
                        images_urls = None

                    # Если не нашли в галерее — берём главное фото
                    if not images_urls:
                        try:
                            images_urls = soup.find('div', class_='single-product-header').find('img').get('src')
                        except Exception:
                            images_urls = None

                            # Сохраняем данные в словарь
                            result_data.append({
                                'Код_товара': None,
                                'Название_позиции': title,
                                'Поисковые_запросы': f'{title}, {search_category}',
                                'Описание': description,
                                'Тип_товара': 'u',
                                'Цена': '',
                                'Цена от': None,
                                'Ярлык': None,
                                'HTML_заголовок': None,
                                'HTML_описание': None,
                                'HTML_ключевые_слова': None,
                                'Валюта': '',
                                'Скидка': '',
                                'Cрок действия скидки от': None,
                                'Cрок действия скидки до': None,
                                'Единица_измерения': '',
                                'Минимальный_объем_заказа': None,
                                'Оптовая_цена': None,
                                'Минимальный_заказ_опт': None,
                                'Ссылка_изображения': image_url,
                                'Наличие': '+',
                                'Количество': None,
                                'Производитель': None,
                                'Страна_производитель': None,
                                'Номер_группы': '',
                                'Адрес_подраздела': None,
                                'Возможность_поставки': None,
                                'Срок_поставки': None,
                                'Способ_упаковки': None,
                                'Личные_заметки': '',
                                'Продукт_на_сайте': None,
                                'Код_маркировки_(GTIN)': None,
                                'Номер_устройства_(MPN)': None,
                                'Идентификатор_товара': sku,
                                'Уникальный_идентификатор': None,
                                'Идентификатор_подраздела': None,
                                'Идентификатор_группы': '',
                                'Подарки': None,
                                'ID_Подарков': None,
                                'Сопутствующие': None,
                                'ID_Сопутствующих': None,
                                'ID_группы_разновидностей': None,
                                'Название_Характеристики': None,
                                'Измерение_Характеристики': None,
                                'Значение_Характеристики': None,
                                'Ссылка_на_товар_на_сайте': None,
                            })

                print(f'Обработано: {product_url}')

    return result_data




def main():
    """
    Главная функция:
    1. Загружает список товаров из JSON
    2. Собирает данные по каждому товару
    3. Сохраняет результат в Excel
    """
    # product_data_list = get_products_urls(url="https://neftemash-m.com/catalog/", headers=headers)
    result_data = get_products_data(file_path='data/product_data_list.json')
    save_excel(data=result_data, species='products')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
