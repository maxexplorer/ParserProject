import json
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

from data.data import category_urls_list

start_time = datetime.now()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

processed_urls = set()

# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(
            soup.find('div', class_='catalog-pagination d-flex').find_all('li')[-1].find('a').get('href').split('=')[-1])
    except Exception:
        pages = 1

    return pages


# Функция получения ссылок товаров
def get_products_urls(category_urls_list: list, headers: dict) -> None:
    with Session() as session:
        for category_url in category_urls_list:
            products_urls = []

            print(f'Обрабатывается ссылка: {category_url}')

            try:
                time.sleep(randint(1, 3))
                html = get_html(url=category_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                category_page_url = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(randint(1, 3))
                    html = get_html(url=category_page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{category_page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find('div',
                                              class_='catalog-items loaded').find_all('div', class_='position-relative')
                    for product_item in product_items:
                        try:
                            product_url = product_item.find('a').get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        products_urls.append(product_url)

                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            get_products_data(products_urls=products_urls, headers=headers)

            print(f'Обработана ссылка: {category_url}')


# Функция получения данных товаров
def get_products_data(products_urls: list, headers: dict) -> None:
    result_data = []

    count_urls = len(products_urls)

    print(f'Всего: {count_urls} товаров!')

    with Session() as session:
        for i, product_url in enumerate(products_urls, 1):
            try:
                time.sleep(randint(1, 3))
                html = get_html(url=product_url, headers=headers, session=session)

            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:




            result_data.append(
                {
                    '№': None,
                    'Артикул': product_id,
                    'Название товара оригинальное': product_name_original,
                    'Название товара': product_name,
                    'Цена, руб.*': price,
                    'Цена до скидки, руб.': price,
                    'НДС, %*': None,
                    'Включить продвижение': None,
                    'Ozon ID': product_id,
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
                    'Объединить на одной карточке*': product_id,
                    'Цвет товара*': None,
                    'Российский размер*': size,
                    'Размер производителя': size,
                    'Статус наличия': status_size,
                    'Название цвета': None,
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
                    'Вид принта': None,
                    'Аннотация': description,
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

            print(f'Обработано: {i}/{count_urls} товаров!')

        save_excel(data=result_data)


# Функция для записи данных в формат xlsx
def save_excel(data: list, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_products_arkonasports_{region}.xlsx'

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
    get_products_urls(category_urls_list=category_urls_list, headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
