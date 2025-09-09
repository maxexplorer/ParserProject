import os
import time
from datetime import datetime
import json

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

# Засекаем время работы программы
start_time = datetime.now()

# Заголовки для HTTP-запросов
headers = {
    'accept': 'application/json',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://lombard-perspectiva.ru',
    'priority': 'u=1, i',
    'referer': 'https://lombard-perspectiva.ru/',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}


def get_html(url: str, headers: dict, session: Session) -> str | None:
    """
    Загружает HTML-код страницы по переданному URL.

    :param url: Адрес страницы для загрузки.
    :param headers: HTTP-заголовки запроса.
    :param session: Сессия requests для повторного использования соединений.
    :return: HTML-код страницы (str) или None, если произошла ошибка.
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


def get_unique_urls(file_path: str) -> set:
    """
    Читает файл с URL-адресами, удаляет дубликаты и сохраняет только уникальные.

    :param file_path: Путь к файлу с URL-адресами.
    :return: Множество уникальных URL.
    """
    # Читаем все строки файла и убираем дубликаты через set
    with open(file_path, 'r', encoding='utf-8') as file:
        unique_urls = set(line.strip() for line in file)

    # Перезаписываем файл только уникальными ссылками
    with open(file_path, 'w', encoding='utf-8') as file:
        print(*unique_urls, file=file, sep='\n')

    return unique_urls


def get_product_urls(headers: dict) -> list[dict]:
    """
    Собирает ссылки на товары по категориям.

    :param category_dict: Словарь со ссылками на страницы каталога
    :param headers: Заголовки запроса
    :return: Список словарей {имя_категории: [список ссылок на товары]}
    """

    product_urls_list = []
    pages = 17

    # Создаем Session для ускорения запросов
    with Session() as session:
        for page in range(1, pages + 1):
            page_url = f"https://lombard-perspectiva.ru/clocks_today/?page={page}"
            try:
                time.sleep(1)
                html = get_html(url=page_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{page_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                # Ищем карточки товаров
                product_items = soup.find('div', class_='elements-container').find_all('a',
                                                                                       class_='product-list-item catalog-item')
            except Exception as ex:
                print(f'product_items: {page_url} - {ex}')
                continue

            # Обрабатываем каждый товар
            for product_item in product_items:
                try:
                    product_url = product_item.get('href')
                except Exception:
                    product_url = None

                if product_url:
                    product_urls_list.append(product_url)

            print(f'Обработано страниц: {page}/{pages}')

    # Сохраняем список ссылок в txt формат
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*product_urls_list, file=file, sep='\n')

    return product_urls_list


def get_products_data(file_path: str, headers: dict) -> list[dict]:
    """
    Загружает данные о товарах с сайта monetnik.ru и сохраняет в Excel партиями.

    :param headers: HTTP-заголовки для запросов.
    :return: Список словарей с данными о товарах.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(product_urls_list)
    batch_size = 100  # сколько строк сохранять за раз
    result_data = []

    with Session() as session:
        # Перебор страниц каталога
        for i, product_url in enumerate(product_urls_list, 1):
            try:
                time.sleep(1)  # задержка, чтобы не забанили

                response = session.get(
                    f"https://backend.lombard-perspectiva.ru/api{product_url}",
                    headers=headers)

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')

                json_data = response.json()

            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            data = json_data['data']

            brand = data.get('brandTitle')

            collection = data.get('collectionTitle')

            reference = data.get('reference')

            product_id = data.get('id')

            prices = data.get('prices')

            price_start = prices.get('start', {}).get('value')
            price_rub = prices.get('rub', {}).get('value')
            price_eur = prices.get('eur', {}).get('value')
            price_usd = prices.get('usd', {}).get('value')

            attributes = data.get('dataAttributes')

            for attribute in attributes:
                if attribute.get('label') == 'Материал корпуса':
                    material = attribute.get('value')
                else:
                    continue

            # Добавляем данные в результирующий список
            result_data.append(
                {
                    'Бренд': brand,
                    'Коллекция': collection,
                    'Название товара': f'{brand} {reference} (id {product_id})',
                    'Стартовая цена: USD': price_start,
                    'Цена: RUB': price_rub,
                    'Цена: EUR': price_eur,
                    'Цена: USD': price_usd,
                    'Материал корпуса': material,
                    'Ссылка':  f"https://lombard-perspectiva.ru{product_url}",

                }
            )

        print(f'Обработано товаров: {i}/{count_urls}')

        # Сохраняем партию данных в Excel
        if len(result_data) >= batch_size:
            save_excel(result_data)
            result_data.clear()

    # Сохраняем остаток
    if result_data:
        save_excel(result_data)

    return result_data


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл (results/result_data.xlsx).

    :param data: Список словарей с данными о товарах.
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    # Если файла нет — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    # Читаем существующие данные
    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    # Преобразуем новые данные в DataFrame
    new_df = DataFrame(data)

    # Дописываем новые строки в конец
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows + 1,
            header=(num_existing_rows == 0),
            sheet_name='Data',
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def main():
    """
    Основная функция: запускает сбор данных и сохраняет их в Excel.
    """
    # get_product_urls(headers=headers)
    # get_unique_urls(file_path='data/product_urls_list.txt')  # если нужно почистить от дублей
    get_products_data(file_path='data/product_urls_list.txt', headers=headers)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
