import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math
import json
import glob

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

from openpyxl import load_workbook, Workbook

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


def read_avito_data(avito_folder: str = "avito") -> dict:
    """
    Чтение данных из Excel файла Avito в указанной папке.
    Берёт первый найденный файл *.xlsx.

    Args:
        avito_folder (str): Папка, где лежит Excel.

    Returns:
        dict: Словарь {артикул: цена}.
    """
    files = glob.glob(os.path.join(avito_folder, "*.xlsx"))
    if not files:
        raise FileNotFoundError(f"В папке {avito_folder} не найдено *.xlsx файлов")

    avito_file = files[0]  # берем первый файл
    print(f"[INFO] Используется файл Avito: {avito_file}")

    wb_avito = load_workbook(avito_file)
    ws_avito = wb_avito.active
    avito_dict = {}

    for row in ws_avito.iter_rows(min_row=3, max_col=5):
        key = row[1].value  # колонка 2 — артикул
        value = row[3].value  # колонка 4 — цена

        if not key:
            continue

        try:
            avito_dict[key.replace('-', '')] = int(value)
        except Exception as ex:
            print(f'read_avito_data: {key} error: {ex}')
            continue

    return avito_dict

def process_data_files(data_folder, avito_dict):
    """Обработка файлов из папки data и обновление цен"""
    # Итерация по файлам в папке data
    for file_name in os.listdir(data_folder):
        data_file_path = os.path.join(data_folder, file_name)

        print(f'Обрабатывается файл: {file_name}')

        # Проверяем, что это Excel-файл
        if file_name.endswith(('.xlsx', '.xlsm')):
            try:
                # Загружаем книгу
                workbook = load_workbook(data_file_path)
                sheet_names = workbook.sheetnames
            except Exception as e:
                raise f'Ошибка чтения файла: {e}'

            # Создаем новую книгу для записи результатов конкретного файла
            new_wb = Workbook()
            new_ws = new_wb.active
            new_ws.append(['Артикул', 'Цена', 'Лист'])  # Заголовки

            # Проходим по листам, начиная со второго
            for sheet_name in sheet_names:
                if sheet_name == 'Инструкция':  # Пропускаем первый лист
                    continue

                sheet = workbook[sheet_name]

                # Получаем заголовки из первой строки (предположим, заголовки находятся в первой строке)
                headers = [cell.value for cell in sheet[2]]

                # Находим индексы колонок с нужными заголовками
                try:
                    oem_column_index = headers.index('Номер детали OEM')  # Ищем столбец "OEM"
                    price_column_index = headers.index('Цена')  # Ищем столбец "Price"
                except Exception as ex:
                    # print(f'{sheet}: {ex}')
                    continue

                # Поиск и обновление цены
                for row in sheet.iter_rows(min_row=5):  # min_row=3 пропускает заголовок
                    try:
                        article_cell = row[oem_column_index].value  # Колонка с артикулом
                        article_cell = article_cell.replace('-', '')
                    except Exception:
                        continue

                    try:
                        price_cell = int(row[price_column_index].value)  # Колонка с ценой
                    except Exception as ex:
                        print(f'price_cell: {article_cell} error: {ex}')
                        continue

                    if article_cell in avito_dict:
                        # Обновляем цену
                        new_price = avito_dict[article_cell]

                        if isinstance(price_cell, int) and isinstance(new_price, int):
                            if price_cell != new_price:
                                row[price_column_index].value = new_price  # Колонка с ценой

                                # Записываем в новый файл
                                new_ws.append([article_cell, new_price, sheet_name])
                        else:
                            print(
                                f"Не удалось сравнить значения: {price_cell} ({type(price_cell)}), {new_price} ({type(new_price)})")

            # Сохраняем изменения в исходный файл
            workbook.save(data_file_path)

            # Сохраняем результаты
            save_results(new_wb=new_wb, file_name=file_name)


def save_results(new_wb, file_name):
    """Сохранение результатов в файл"""
    data = 'results'

    if not os.path.exists(data):
        os.mkdir(data)

    result_file_path = f'results/updated_prices_{file_name}'

    new_wb.save(result_file_path)


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл, добавляя новые строки к существующему листу.

    :param data: Список словарей с данными о товарах
    :param category_name: Название категории для формирования имени файла
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'
    sheet_name = 'avito'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    df_existing = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name=sheet_name, index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_product_card(products_data: dict):
    pass


def get_products_data(seller_urls: list, limit: int = 100) -> None:
    """
    Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel.

    :param category_dict: Словарь категорий и их URL
    :param batch_size: Количество товаров на страницу
    """

    # product_data_list = []

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
            # first_params = {
            #     'p': 1,
            #     'sellerId': seller_id,
            # }

            first_params = {
                'p': 1,
                'sellerId': seller_id,
                'itemsOnPage': limit,
                'limit': limit,
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
                total = json_data.get('foundCount', 0)
                if total == 0:
                    print(f"{seller_url}: товаров нет")
                    continue

                pages = math.ceil(total / limit)

                if pages > 100:
                    pages = 100

                print(f"{seller_url}: всего {total} товаров, {pages} страниц")

            except Exception as ex:
                print(f"{seller_url}: ошибка получения total: {ex}")
                continue

            product_urls = []
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
                    item: dict

                    title = item.get('title')

                    if title is None or title == '':
                        continue

                    article_list = item.get('iva', {}).get('SparePartsParamsStep') or []
                    article = article_list[0].get('payload', {}).get('text') if article_list else None

                    if article is None or article == '':
                        continue

                    brand_list = item.get('iva', {}).get('AutoPartsManufacturerStep') or []
                    brand = brand_list[0].get('payload', {}).get('value') if brand_list else None

                    if brand is None or brand == '':
                        continue

                    prices = item.get('priceDetailed')

                    if prices is None or prices == []:
                        continue

                    price = prices.get('value')

                    product_url = f"https://www.avito.ru{item.get('urlPath')}"

                    product_urls.append(product_url)

                    result_list.append(
                        {
                            'Название': title,
                            'Артикул': article,
                            'Бренд': brand,
                            'Цена': price,
                            'Ссылка': product_url
                        }
                    )

                print(f'Обработано страниц: {page}/{pages}')

            # Сохраняем в Excel
            save_excel(data=result_list)

            print(f"{seller_url}: данные сохранены, {len(result_list)} записей")

    #         product_data_list.append({seller_url: product_url})
    #
    # # Сохраняем список ссылок в JSON
    # directory = 'data'
    # os.makedirs(directory, exist_ok=True)
    #
    # with open('data/product_data_list.json', 'w', encoding='utf-8') as file:
    #     json.dump(product_data_list, file, indent=4, ensure_ascii=False)
    #
    # return product_data_list


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
