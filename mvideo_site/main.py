import os
import time
from datetime import datetime
import json

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

from configs.config import headers, cookies

# Засекаем время работы программы
start_time = datetime.now()


def get_html(url: str, headers: dict, session: Session) -> str | None:
    """
    Загружает HTML-код страницы по переданному URL.

    :param url: адрес страницы для загрузки
    :param headers: словарь с HTTP-заголовками
    :param session: объект requests.Session для повторного использования соединений
    :return: HTML-код страницы (str) или None при ошибке
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f'status_code: {response.status_code}')
        return response.text
    except Exception as ex:
        print(f'get_html: {ex}')
        return None


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML-кода.

    Аргументы:
        html: HTML-код страницы категории.

    Возвращает:
        Целое число — количество страниц пагинации.
        Если пагинация не найдена, возвращает 1.
    """
    soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу в блоке пагинации
        pages: int = int(soup.find('div', class_='module-pagination').find_all('a')[-2].get_text(strip=True))
        return pages
    except Exception:
        # Если пагинации нет — возвращаем 1
        return 1


def get_categories_data(headers: dict, cookies: dict) -> None:
    categories_data = []

    with Session() as session:
        try:
            response = session.get('https://www.mvideo.ru/bff/settings/v2/catalog', cookies=cookies, headers=headers)

            json_data = response.json()
        except Exception as ex:
            print(f'get_categories_data: {ex}')

        try:
            main_category_items = json_data['body']['categories']
        except Exception:
            main_category_items = []

        for main_category_item in main_category_items:
            main_category_name = main_category_item.get('name')
            category_items = main_category_item.get('categories', [])
            for category_item in category_items:
                category_name = category_item.get('name')
                subcategory_items = category_item.get('categories', [])
                for subcategory_item in subcategory_items:
                    subcategory_name = subcategory_item.get('categories')

        if not json_data:
            raise 'not json_data'

    # Сохраняем список ссылок в JSON
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/category_data.json', 'w', encoding='utf-8') as file:
        json.dump(categories_data, file, indent=4, ensure_ascii=False)


def get_products_data(file_path: str, headers: dict) -> list:
    """
    Загружает данные о товарах с API сайта и сохраняет их партиями в Excel.

    :param file_path: путь к файлу с URL товаров
    :param headers: словарь с HTTP-заголовками
    :return: список словарей с данными о товарах
    """
    # Читаем product_data_list из JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        category_data: list = json.load(file)

    batch_size = 1000
    result_data = []

    with Session() as session:
        for category_dict in category_data:
            category_name, category_url = next(iter(category_dict.items()))

            print(f'Обработка категории: {category_name}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_data: {ex}')

            if not html:
                continue

            # Определяем количество страниц
            pages: int = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url: str = f"{category_url}?PAGEN_2={page}"

                try:
                    time.sleep(1)  # Задержка, чтобы не перегружать сайт
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find_all('div',
                                                  class_='item_block col-4 col-md-3 col-sm-6 col-xs-6 js-notice-block')
                except Exception as ex:
                    print(f'product_items: {ex}')
                    continue

                for product_item in product_items:
                    try:
                        product_name = product_item.find('div', class_='item-title').find('span').get_text(strip=True)
                    except Exception:
                        product_name = ''

                    try:
                        model = product_item.find('img', class_='img-responsive').get('title')
                    except Exception:
                        model = ''

                    brands_with_two_words = ['De Dietrich', 'Jet Air']
                    model_lower = model.lower()

                    if any(b.lower() in model_lower for b in brands_with_two_words):
                        brand = ' '.join(model.split()[:2])
                    else:
                        brand = model.split()[0]

                    # Удаляем бренд из строки model
                    model_clean = model.replace(brand, '').strip()

                    # Удаляем model из строки product_name
                    product_name_clean = product_name.replace(model, '').strip()

                    if len(product_name_clean) == 0:
                        product_name_clean = category_name

                    try:
                        price = product_item.find('span', class_='price_value').get_text(strip=True)
                    except Exception:
                        price = ''

                    result_data.append({
                        'Товар': product_name_clean,
                        'Бренд': brand,
                        'Модель': model_clean,
                        'Цена': price,

                    })

                    if len(result_data) >= batch_size:
                        save_excel(result_data)
                        result_data.clear()

                print(f'Обработано страниц: {page}/{pages}')

    if result_data:
        save_excel(result_data)

    return result_data


def save_excel(data: list) -> None:
    """
    Сохраняет список товаров в Excel (results/result_data.xlsx).

    :param data: список словарей с данными о товарах
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1,
                        header=(num_existing_rows == 0),
                        sheet_name='Data', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main():
    """
    Основная функция программы.
    Собирает данные о товарах и сохраняет их в Excel.
    """

    get_categories_data(headers=headers, cookies=cookies)
    # get_products_data(file_path='data/category_data.json', headers=headers)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
