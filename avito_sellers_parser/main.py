import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import seller_urls

start_time = datetime.now()


def get_seller_id(url: str) -> str | None:
    """
    Извлекает sellerId из ссылки Avito.

    Args:
        url (str): ссылка вида https://www.avito.ru/...&sellerId=XXXX

    Returns:
        str | None: значение sellerId или None, если параметр не найден.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    seller_id = query_params.get("sellerId")
    return seller_id[0] if seller_id else None


def save_excel(data: list[dict], seller_id: str) -> None:
    """
    Сохраняет список данных в Excel-файл, добавляя новые строки к существующему листу.

    :param data: Список словарей с данными о товарах
    :param category_name: Название категории для формирования имени файла
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=seller_id, index=False)

    df_existing = read_excel(file_path, sheet_name=seller_id)
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name=seller_id, index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_products_data(seller_urls: list, batch_size: int = 12) -> None:
    """
    Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel.

    :param category_dict: Словарь категорий и их URL
    :param batch_size: Количество товаров на страницу
    """

    with Session() as session:
        for seller_url in seller_urls:
            seller_id = get_seller_id(url=seller_url)

            headers = {
                'accept': 'application/json',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'priority': 'u=1, i',
                'referer': seller_url,
                'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'x-source': 'client-browser',
            }

            # Параметры запроса для первой страницы
            first_params = {
                'p': 1,
                'sellerId': seller_id,
            }

            try:
                time.sleep(1)
                response = session.get(
                    'https://www.avito.ru/web/1/profile/items',
                    params=first_params,
                    headers=headers,
                    timeout=(3, 5)
                )

                if response.status_code != 200:
                    print(f' seller_url: {seller_url}: статус ответа {response.status_code}')
                    continue

                json_data: dict = response.json()
                total = json_data.get('totalCount', 0)
                if total == 0:
                    print(f"{seller_url}: товаров нет")
                    continue

                pages = math.ceil(total / batch_size)

                if pages > 100:
                    pages = 100

                print(f"{seller_url}: всего {total} товаров, {pages} страниц")

            except Exception as ex:
                print(f"{seller_url}: ошибка получения total: {ex}")
                continue

            result_list = []

            # Проходим по всем страницам
            for page in range(1, pages + 1):
                params = first_params.copy()
                params['p'] = page

                try:
                    time.sleep(1)
                    response = session.get(
                        'https://www.avito.ru/web/1/profile/items',
                        params=params,
                        headers=headers,
                        timeout=(3, 5)
                    )

                    if response.status_code != 200:
                        print(f' seller_url: {seller_url}: статус ответа {response.status_code}')
                        continue

                    json_data: dict = response.json()
                    items: list = json_data.get('catalog', {}).get('items', [])

                except Exception as ex:
                    print(f"{seller_url} страница {page}: {ex}")
                    continue

                if not items:
                    print(f'not data page: {page}')
                    continue

                # Обрабатываем товары на странице
                for item in items:
                    title = item.get('title')

                    if title is None or title == '':
                        continue

                    prices = item.get('priceDetailed')

                    if prices is None or prices == []:
                        continue

                    price = prices.get('value')

                    result_list.append(
                        {
                            'Название': title,
                            'Цена': price,
                        }
                    )

                print(f'Обработано страниц: {page}/{pages}')

            # Сохраняем в Excel
            save_excel(data=result_list, seller_id=seller_id)

            print(f"{seller_url}: данные сохранены, {len(result_list)} записей")


def main() -> None:
    """
    Точка входа в программу. Запускает обработку категорий и сбор данных о товарах.
    """

    get_products_data(seller_urls=seller_urls)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
