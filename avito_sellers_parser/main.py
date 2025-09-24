import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math
import json
import glob
import re

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel
from openpyxl import load_workbook

start_time = datetime.now()

seller_urls = [
    "https://www.avito.ru/brands/ladyapartsspb/items/all?s=profile_search_show_all&sellerId=40f4b7a6e761189ef00b2774303df3bd",
    # "https://www.avito.ru/brands/i26983653/all/zapchasti_i_aksessuary?gdlkerfdnwq=101&shopId=43050&page_from=from_item_card&iid=7298163664&sellerId=f6971b162668ccde657d1aea1c4f3335"
]


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


def read_avito_data(avito_folder: str = 'avito') -> dict:
    """
    Чтение данных из Excel файла Avito в указанной папке.
    Берёт первый найденный файл *.xlsx.
    Возвращает словарь {артикул: {'Бренд': ..., 'Цена': ..., 'Ссылка': ...}}.
    """
    files = glob.glob(os.path.join(avito_folder, "*.xlsx"))
    if not files:
        raise FileNotFoundError(f'В папке {avito_folder} не найдено *.xlsx файлов')

    avito_file = files[0]  # берем первый файл
    print(f'[INFO] Используется файл Avito: {avito_file}')

    df = read_excel(avito_file, header=1, sheet_name=0)
    avito_dict = {}

    # Артикул во 2 колонке, бренд в колонке 'Бренд', цена в колонке 'Цена', ссылка в колонке 'Ссылка'
    for _, row in df.iterrows():
        article = str(row[df.columns[1]]).replace('-', '').strip()  # колонка 2
        brand = row.get('Бренд')
        price = row.get('Цена')
        url = row.get('Ссылка')
        if article:
            avito_dict[article] = {'Бренд': brand, 'Цена': price, 'Ссылка': url}

    return avito_dict


def get_normalize_article(article: str) -> str | None:
    if not article:
        return None

    # Если есть символ "•", берем часть после него
    if '•' in article:
        article = article.split('•')[-1]

    # Убираем "-L" в конце, если есть
    if article.endswith('-L'):
        article = article[:-2]

    # Убираем пробелы и дефисы в середине
    article = re.sub(r'[\s-]', '', article)

    return article.strip()


def save_excel(data: list[dict], seller_id: str) -> None:
    """
    Сохраняет список данных в Excel-файл, добавляя новые строки к существующему листу.

    :param data: Список словарей с данными о товарах
    :param category_name: Название категории для формирования имени файла
    """
    directory = 'avito'
    file_path = f'{directory}/result_data_{seller_id}.xlsx'
    sheet_name = "data"

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


def process_data_files(avito_dict: dict, data_folder='data'):
    """
    Обработка файлов из папки data и обновление данных по артикулу.
    Артикул находится во 2 колонке. Если найден в avito_dict, записываем
    Бренд, Цена и Ссылка в соответствующие колонки.
    Только недостающие колонки добавляются.

    Заголовки находятся во 2-й строке.
    """
    excel_files = glob.glob(os.path.join(data_folder, "*.xls*"))

    for data_file_path in excel_files:
        file_name = os.path.basename(data_file_path)
        print(f'[INFO] Обрабатывается файл: {file_name}')

        try:
            wb = load_workbook(data_file_path)
            sheet_names = wb.sheetnames
        except Exception as e:
            print(f'[ERROR] Ошибка чтения файла {file_name}: {e}')
            continue

        for sheet_name in sheet_names:
            ws = wb[sheet_name]

            # Получаем существующие заголовки из 2-й строки
            headers = [cell.value for cell in ws[2]]

            # Колонки, которые нужно добавить, если их нет
            new_cols = ['Бренд', 'Цена', 'Ссылка']
            col_indices = {}

            for col in new_cols:
                if col not in headers:
                    # Добавляем колонку в конец текущих заголовков
                    ws.cell(row=2, column=len(headers) + 1, value=col)  # <-- исправлено row=2
                    col_indices[col] = len(headers) + 1
                    headers.append(col)
                else:
                    col_indices[col] = headers.index(col) + 1

            # Проходим по всем строкам, начиная с 3-й (данные)
            for row in ws.iter_rows(min_row=3, max_col=len(headers)):
                article_cell = row[1].value  # колонка 2
                if not article_cell:
                    continue
                article = str(article_cell).replace('-', '').strip()

                if article in avito_dict:
                    ws.cell(row=row[0].row, column=col_indices['Бренд'], value=avito_dict[article]['Бренд'])
                    ws.cell(row=row[0].row, column=col_indices['Цена'], value=avito_dict[article]['Цена'])
                    ws.cell(row=row[0].row, column=col_indices['Ссылка'], value=avito_dict[article]['Ссылка'])

        wb.save(data_file_path)
        print(f"[INFO] Файл обновлён: {file_name}")


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

                # if pages > 100:
                #     pages = 100

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

                    normalize_article = get_normalize_article(article)

                    if normalize_article is None or normalize_article == '':
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
                            'Артикул': normalize_article,
                            'Бренд': brand,
                            'Цена': price,
                            'Ссылка': product_url
                        }
                    )

                print(f'Обработано страниц: {page}/{pages}')

            # Сохраняем в Excel
            save_excel(data=result_list, seller_id=seller_id)

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

    # get_products_data(seller_urls=seller_urls)
    avito_dict = read_avito_data()
    process_data_files(avito_dict=avito_dict)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
