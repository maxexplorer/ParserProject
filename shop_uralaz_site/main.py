import os
import time
from datetime import datetime
import json
import re

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import category_data_list

# Засекаем время запуска программы
start_time = datetime.now()

# Заголовки HTTP-запросов (имитация браузера)
headers: dict[str, str] = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}


def get_html(url: str, headers: dict[str, str], session: Session) -> str | None:
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

        html: str = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')
        return None


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML.

    :param html: HTML код страницы
    :return: Количество страниц (если не найдено — возвращает 1 по умолчанию)
    """
    soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу пагинации
        page: int = int(soup.find('div', class_='pagination-block').find_all('a')[-2].get_text(strip=True))
        return page
    except Exception:
        return 1


def get_products_urls(category_data_list: list[dict], headers: dict[str, str]) -> list[dict]:
    """
    Собирает ссылки на товары по категориям.

    :param category_data_list: Список словарей с данными категорий (group_number и category_url)
    :param headers: Заголовки запроса
    :return: Список словарей с номерами группы и списком ссылок на товары
    """
    product_data_list: list[dict] = []

    # Создаем Session для ускорения запросов
    with Session() as session:
        for category_data in category_data_list:
            group_number: int = category_data['group_number']
            category_url: str = category_data['category_url']
            product_urls: list[str] = []

            try:
                html: str | None = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_urls: {category_url} - {ex}')
                continue

            pages: int = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url: str = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

                # Получаем список товаров на странице
                try:
                    product_items = soup.find_all('div', class_='item-product__info')
                except Exception as ex:
                    print(f'data: {ex}')
                    product_items = []

                # Перебираем товары
                for product_item in product_items:
                    try:
                        product_url: str = f"https://shop.uralaz.ru{product_item.find('a').get('href')}"
                    except Exception:
                        product_url = ''

                    if product_url:
                        product_urls.append(product_url)

                print(f'Обработано страниц: {page}/{pages}')

            # Добавляем словарь в итоговый список
            product_data_list.append({
                "group_number": group_number,
                "product_urls": product_urls
            })

            print(f'Обработана категория: {category_url}')

    # Сохраняем список словарей в JSON
    directory: str = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/product_data_list.json', 'w', encoding='utf-8') as file:
        json.dump(product_data_list, file, indent=4, ensure_ascii=False)

    return product_data_list


def save_excel(data: list[dict], category_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о товарах
    :param category_name: Имя категории для имени файла
    """
    directory: str = 'results'
    file_path: str = f'{directory}/result_data_{category_name}.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Export Products Sheet', index=False)

    df_existing: DataFrame = read_excel(file_path, sheet_name='Export Products Sheet')
    num_existing_rows: int = len(df_existing.index)

    new_df: DataFrame = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Export Products Sheet', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_products_data(category_data_list: list[dict], headers: dict[str, str]) -> None:
    """
    Извлекает данные о товарах (название, описание, характеристики, фото и т.д.)
    и сохраняет их в Excel-файлы по категориям.

    :param category_data_list: Список словарей с данными категорий
    :param headers: Заголовки запроса
    """
    # Создаем requests.Session для ускорения
    with Session() as session:
        # Итерируемся по категориям
        for category_data in category_data_list:
            category_name: str = category_data['category_name']
            group_number: int = category_data['group_number']
            category_url: str = category_data['category_url']

            result_data: list[dict] = []

            try:
                html: str | None = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_data: {category_url} - {ex}')
                continue

            pages: int = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url: str = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

                # Получаем список товаров на странице
                try:
                    product_items = soup.find_all('div', class_='product-list__item item-product')
                except Exception as ex:
                    print(f'data: {ex}')
                    product_items = []

                # Перебираем товары
                for product_item in product_items:
                    # Название товара
                    try:
                        name: str = product_item.find('a', class_='item-product__name').get_text(strip=True)
                    except Exception:
                        name = ''

                    try:
                        sku: str = product_item.find('div', class_='item-product__designation').get_text(strip=True)
                    except Exception:
                        sku = ''

                    if sku is None:
                        sku = name

                    # Характеристики товара
                    try:
                        characteristic_items = product_item.find('div', class_='item-product__props props-item-product') \
                            .find_all('div', class_='props-item-product__item prop-item-product')

                        characteristics_str: str = ''
                        for characteristic_item in characteristic_items:
                            prop_name: str = characteristic_item.find('span', class_='prop-item-product__name').get_text(
                                strip=True)
                            prop_value: str = characteristic_item.find('span', class_='prop-item-product__value').get_text(
                                strip=True)

                            # Добавляем только если значение не пустое и не равно '0'
                            if prop_value and prop_value != '0':
                                characteristics_str += f'{prop_name} {prop_value}; '

                        characteristics: str = characteristics_str.strip('; ')

                    except Exception:
                        characteristics = ''

                    # Изображения
                    try:
                        content_url: str = product_item.find('img', itemprop='contentUrl').get('src')
                        resized_img_url: str = re.sub(r"/\d+_\d+_\d+/", "/480_480_0/", content_url)
                        image_url: str = f"https://shop.uralaz.ru{resized_img_url}"
                    except Exception:
                        image_url = ''

                    # Сохраняем данные в словарь
                    result_data.append({
                        'Код_товара': None,
                        'Название_позиции': name,
                        'Поисковые_запросы': f'{name}, {category_name}',
                        'Описание': characteristics,
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
                        'Номер_группы': group_number,
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

                print(f'Обработано страниц: {page}/{pages}')

            save_excel(data=result_data, category_name=category_name)


def main() -> None:
    """
    Главная функция:
    1. Загружает список категорий
    2. Собирает данные по каждому товару
    3. Сохраняет результат в Excel
    """
    # Сбор данных по товарам
    get_products_data(category_data_list=category_data_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
