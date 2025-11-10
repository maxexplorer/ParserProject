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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://trial-sport.ru/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


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
        pages: int = int(
            soup.find('div', class_='paging b30').find('td', {'align': 'right'}).find_all('a')[-2].get_text(strip=True))
        return pages
    except Exception:
        # Если пагинации нет — возвращаем 1
        return 1


def get_category_urls(url: str, headers: dict) -> None:
    with Session() as session:
        try:
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f'get_category_urls: {ex}')

        if not html:
            raise 'not html'

        soup = BeautifulSoup(html, 'lxml')

        category_urls = []

        product_items = soup.find('div', class_='catalog catalog_active').find_all('span')

        for product_item in product_items:
            try:
                product_name = product_item.get_text(strip=True)
            except Exception:
                product_name = None
            try:
                product_url = f"https://trial-sport.ru{product_item.find('a').get('href')}"
            except Exception:
                product_url = None
            category_urls.append(
                product_url
            )

    # Сохраняем список ссылок в JSON
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open(f'{directory}/category_urls.txt', 'w', encoding='utf-8') as file:
        print(*category_urls, file=file, sep='\n')


def get_products_data(file_path: str, headers: dict) -> list:
    """
    Загружает данные о товарах с API сайта и сохраняет их партиями в Excel.

    :param file_path: путь к файлу с URL товаров
    :param headers: словарь с HTTP-заголовками
    :return: список словарей с данными о товарах
    """
    # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
    with open(file_path, 'r', encoding='utf-8') as file:
        category_urls = [line.strip() for line in file]

    batch_size = 1000
    result_data = []

    with Session() as session:
        for i, category_url in enumerate(category_urls[:3], 1):
            count_urls = len(category_urls)
            print(f'Обработка категории: {i}/{count_urls}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_data: {ex}')

            if not html:
                continue

            # Определяем количество страниц
            pages: int = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url: str = f"{category_url}&pg={page}"

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
                    product_items = soup.find_all('div', class_='object ga')
                except Exception as ex:
                    print(f'product_items: {ex}')
                    continue

                for product_item in product_items:
                    try:
                        title = product_item.find('a', class_='title').find('span').find('font')
                    except Exception:
                        title = ''

                    try:
                        name = title.get_text(strip=True)
                    except Exception:
                        name = ''

                    try:
                        model = title.next_sibling.strip()
                    except Exception:
                        model = ''

                    try:
                        brand = product_item.find('span', class_='brand').find('span', class_='blue').get_text(strip=True)
                    except Exception:
                        brand = ''

                    try:
                        price = int(''.join(filter(lambda x: x.isdigit(), product_item.find(
                            'span', class_='price').find('span', class_='value').get_text(strip=True))))
                    except Exception:
                        price = ''

                    discount_spans = product_item.find_all('span', class_='discount')
                    discount_price = ''
                    discountsale_price = ''

                    for span in discount_spans:
                        value_tag = span.find('span', class_='value')
                        if value_tag:
                            value = int(''.join(filter(str.isdigit, value_tag.get_text(strip=True))))
                            # В зависимости от класса span определяем, что это:
                            if 'discountsale' in span.get('class', []):
                                discountsale_price = value
                            else:
                                discount_price = value

                    result_data.append({
                        'Товар': name,
                        'Бренд': brand,
                        'Модель': model,
                        'Цена': price,
                        'Цена по дисконтной карте': discount_price,
                        'Цена со скидкой': discountsale_price

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

    # get_category_urls(url="https://trial-sport.ru/catalog.html", headers=headers)
    get_products_data(file_path='data/category_urls.txt', headers=headers)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
