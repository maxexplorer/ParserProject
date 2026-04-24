import os
import time
from datetime import datetime
import math

from requests import Session
import pandas as pd
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import category_list

start_time = datetime.now()


def get_basket_number(product_id: int) -> str | None:
    """
    Определяет номер корзины для товара по его ID.

    :param product_id: ID товара
    :return: Номер корзины (строка) или None, если short_id некорректный
    """
    short_id = product_id // 100000

    # Таблица диапазонов корзин
    ranges = [
        (0, 143, '01'),
        (144, 287, '02'),
        (288, 431, '03'),
        (432, 719, '04'),
        (720, 1007, '05'),
        (1008, 1061, '06'),
        (1062, 1115, '07'),
        (1116, 1169, '08'),
        (1170, 1313, '09'),
        (1314, 1601, '10'),
        (1602, 1655, '11'),
        (1656, 1919, '12'),
        (1920, 2045, '13'),
        (2046, 2189, '14'),
        (2190, 2405, '15'),
        (2406, 2621, '16'),
        (2622, 2837, '17'),
        (2838, 3053, '18'),
        (3054, 3269, '19'),
        (3270, 3485, '20'),
        (3486, 3701, '21'),
        (3702, 3917, '22'),
        (3918, 4133, '23'),
        (4134, 4349, '24'),
        (4350, 4565, '25'),
        (4566, 4877, '26'),
        (4878, 5189, '27'),
        (5190, 5501, '28'),
        (5502, 5813, '29'),
        (5814, 6125, '30'),
        (6126, 6437, '31'),
        (6438, 6748, '32'),
        (6749, 7061, '33'),
        (7062, 7373, '34'),
        (7374, 7685, '35'),
        (7686, 7997, '36'),
        (7998, 8309, '37'),
        (8310, 8741, '38'),
        (8742, 9173, '39'),
        (9174, 9605, '40'),
        (9606, 10373, '41'),
        (10374, 11141, '42'),
        (11142, 11909, '43'),
        (11910, float('inf'), '44')
    ]

    for low, high, basket in ranges:
        if low <= short_id <= high:
            return basket

    print(f'Некорректный short_id: {short_id}')
    return None


def get_product_card(product_id: int, session: Session) -> dict | None:
    """
    Получает значение опции "Объем скороварки" для конкретного товара через API корзины.

    :param product_id: ID товара
    :param session: Сессия Session для запросов
    :return: Значение опции или None
    """
    short_id = product_id // 100000
    basket = get_basket_number(product_id=product_id)

    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        'sec-ch-ua-mobile': '?0',
    }

    try:
        time.sleep(0.5)

        response = session.get(
            f'https://basket-{basket}.wbbasket.ru/vol{short_id}/part{product_id // 1000}/{product_id}/info/ru/card.json',
            headers=headers
        )

        if response.status_code != 200:
            print(f'get_product_card: {product_id} status_code: {response.status_code}')
            return None

        json_data = response.json()
        options = json_data.get('options', [])

    except Exception as ex:
        print(f'{product_id}: {ex}')
        return None

    values = {
        opt.get('name'): opt.get('value')
        for opt in options
        if opt.get('name')
    }

    return values


def save_excel(data: list[dict], category_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл, добавляя новые строки к существующему листу.

    :param data: Список словарей с данными о товарах
    :param category_name: Название категории для формирования имени файла
    """
    directory = 'results'
    file_path = f'{directory}/result_data_{category_name}.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Data', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_products_data(category_list: list, batch_size: int = 100) -> None:
    """
    Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel.

    :param category_list: Список категорий
    :param batch_size: Количество товаров на страницу
    """

    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'deviceid': 'site_d65c92c0ae19412c9cf011a89c998cf1',
        'priority': 'u=1, i',
        'referer': 'https://www.wildberries.ru/',
        'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        'x-queryid': 'qid716365611175214577720260421065252',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '14.6.1',
        'x-userid': '0',
    }

    cookies = {
        'wbx-validation-key': '042261a8-d7e3-4266-8343-31fb35d5a295',
        '_wbauid': '7163656111752145777',
        'external-locale': 'ru',
        '_ga': 'GA1.1.1098996660.1758261326',
        '_ga_TXRZMJQDFE': 'GS2.1.s1759146135$o7$g0$t1759146135$j60$l0$h0',
        'routeb': '1776081038.566.2243.203049|fc3b37d75a18d923fd0e9c7589719997',
        'x_wbaas_token': '1.1000.73c8daf45d2242b7983afd5c1cd304b6.MTV8NDUuMTI5LjE0MS4xOTV8TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0Ny4wLjAuMCBTYWZhcmkvNTM3LjM2fDE3Nzc5NjI2NDF8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzc3MzU3ODQxfDE=.MEUCIAZsPQy8q0IwvTBBjDDsWqTbGt7vXxKo13tympPabacDAiEAofCqDQ7Klz2YEC7FkNiQ10Jvva7FAKwzmkmry0FN+54=',
        '_cp': '1',
    }

    with Session() as session:
        for category_name in category_list:

            processed_ids = set()
            brand_none_list = []
            duplicates_count = 0

            # Параметры запроса для первой страницы
            first_params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'lang': 'ru',
                'page': 1,
                'query': category_name,
                'resultset': 'catalog',
                'sort': 'popular',
                'spp': '30',
                'suppressSpellcheck': 'false',
            }

            try:
                time.sleep(0.5)
                response = session.get(
                    'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search',
                    headers=headers,
                    cookies=cookies,
                    params=first_params,
                    timeout=(3, 5)
                )

                if response.status_code != 200:
                    print(f' category_name: {category_name}: статус ответа {response.status_code}')
                    if response.status_code == 498:
                        return
                    continue

                json_data: dict = response.json()
                total = json_data.get('total', 0)
                if total == 0:
                    print(f"{category_name}: товаров нет")
                    continue

                pages = math.ceil(total / batch_size)

                if pages > 100:
                    pages = 100

                print(f"{category_name}: всего {total} товаров, {pages} страниц")

            except Exception as ex:
                print(f"{category_name}: ошибка получения total: {ex}")
                continue

            result_list = []

            # Проходим по всем страницам
            for page in range(1, pages + 1):
                params = first_params.copy()
                params['page'] = page

                try:
                    time.sleep(0.5)
                    response = session.get(
                        'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search',
                        headers=headers,
                        cookies=cookies,
                        params=params,
                        timeout=(3, 5)
                    )

                    if response.status_code != 200:
                        print(f' category_name: {category_name} page: {page} статус ответа: {response.status_code}')
                        continue

                    json_data: dict = response.json()
                    data: list = json_data.get('products', [])

                except Exception as ex:
                    print(f"{category_name} страница {page}: {ex}")
                    continue

                if not data:
                    print(f'not data page: {page}')
                    continue

                # Обрабатываем товары на странице
                for i, item in enumerate(data, 1):

                    count_products = len(data)

                    brand = item.get('brand')

                    product_id = item.get('id')

                    if brand is None or brand == '':
                        brand_none_list.append(product_id)
                        continue

                    name = item.get('name')

                    size = item.get('sizes', [])[0].get('origName')

                    price = item.get('sizes', [])[0].get('price', {}).get('product') // 100

                    if product_id in processed_ids:
                        duplicates_count += 1
                        continue

                    values = get_product_card(product_id=product_id, session=session)

                    if values is None or values == {}:
                        continue

                    processed_ids.add(product_id)

                    result_list.append(
                        {
                            'Название': name,
                            'Бренд': brand,
                            'Цена': price,
                            'Размер': size,
                            **values
                        }
                    )

                    print(f'Page: {page} Products {i}/{count_products}')

                print(f'Processed page: {page}/{pages}')
                print(f'Duplicates: {duplicates_count}')
                print(f'No brands {len(brand_none_list)}')

            # Сохраняем в Excel
            save_excel(result_list, category_name=category_name)

            print(f"{category_name}: данные сохранены, {len(result_list)} записей")


def main() -> None:
    """
    Точка входа в программу. Запускает обработку категорий и сбор данных о товарах.
    """
    get_products_data(category_list=category_list)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
