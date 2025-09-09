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
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/139.0.0.0 Safari/537.36'
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


def get_products_data(headers: dict) -> list[dict]:
    """
    Загружает данные о товарах с сайта monetnik.ru и сохраняет в Excel партиями.

    :param headers: HTTP-заголовки для запросов.
    :return: Список словарей с данными о товарах.
    """
    batch_size = 1000  # сколько строк сохранять за раз
    result_data = []

    with Session() as session:
        # Перебор страниц каталога
        for page in range(1, 1147):
            products_urls_list = []
            page_url = f"https://www.monetnik.ru/monety/page.{page}/"

            try:
                time.sleep(1)  # задержка, чтобы не забанили
                html = get_html(url=page_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{page_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                # Ищем карточки товаров
                product_items = soup.find_all('div', class_='product__card--quick track-merchandising')
            except Exception as ex:
                print(f'product_card_info: {page_url} - {ex}')
                continue

            # Обрабатываем каждый товар
            for product_item in product_items:
                try:
                    product_name = product_item.find('span', class_='product__card-name').get_text(strip=True)
                except Exception:
                    product_name = None

                try:
                    price = ''.join(filter(
                        lambda x: x.isdigit(),
                        product_item.find('div', class_='product__card-prices').next.get_text(strip=True)
                    ))
                except Exception:
                    price = None

                try:
                    old_price = ''.join(filter(
                        lambda x: x.isdigit(),
                        product_item.find('span', class_='strike').get_text(strip=True)
                    ))
                except Exception:
                    old_price = None

                try:
                    product_url = product_item.find('a', class_='absolute-link').get('href')
                except Exception:
                    product_url = None

                # Сохраняем URL для отдельного списка
                if product_url:
                    products_urls_list.append(product_url)

                # Добавляем данные в результирующий список
                result_data.append(
                    {
                        'Name': product_name,
                        'Price': price,
                        'Old price': old_price,
                        'URL': product_url
                    }
                )

            # Создаем папку для списка URL
            directory = 'data'
            os.makedirs(directory, exist_ok=True)

            # Сохраняем URL в файл
            with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
                print(*products_urls_list, file=file, sep='\n')

            print(f'Обработано страниц: {page}')

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
    # get_unique_urls(file_path='data/products_urls_list.txt')  # если нужно почистить от дублей
    result_data = get_products_data(headers=headers)
    save_excel(data=result_data)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
