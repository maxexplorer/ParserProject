import os
import re
import time
from datetime import datetime
from random import randint

from openpyxl import Workbook, load_workbook
from requests import Response, Session

start_time = datetime.now()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
DEFAULT_429_PAUSE = 5
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE_PATH = os.path.join(BASE_DIR, 'results', 'result_data_4_000_000.xlsx')
RESULT_FILE_PATH = os.path.join(BASE_DIR, 'results', 'result_data_4_000_000_with_products.xlsx')


def get_api_headers(seller_id: int) -> dict:
    return {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.wildberries.ru',
        'priority': 'u=1, i',
        'referer': f'https://www.wildberries.ru/seller/{seller_id}',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': USER_AGENT,
        'x-client-name': 'site',
    }


def get_catalog_headers(seller_id: int) -> dict:
    headers = get_api_headers(seller_id)
    headers.update({
        'deviceid': 'site_d65c92c0ae19412c9cf011a89c998cf1',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '14.15.2',
    })
    return headers


def sleep_if_429(response: Response, seller_id: int, request_name: str) -> bool:
    if response.status_code != 429:
        return False

    retry_after = response.headers.get('Retry-After')
    try:
        pause = int(retry_after) if retry_after else DEFAULT_429_PAUSE
    except ValueError:
        pause = DEFAULT_429_PAUSE

    print(f'Продавец {seller_id}: {request_name} вернул 429. Пауза {pause} секунд, затем повтор')
    time.sleep(pause)
    return True


def extract_seller_id(seller_url: str) -> int | None:
    match = re.search(r'/seller/(\d+)', seller_url)
    if not match:
        return None

    return int(match.group(1))


def load_sellers(file_path: str) -> list[dict]:
    wb = load_workbook(file_path)
    ws = wb['Sellers'] if 'Sellers' in wb.sheetnames else wb.active
    headers = [cell.value for cell in ws[1]]

    sellers = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_data = dict(zip(headers, row))
        seller_url = row_data.get('Ссылка')
        if seller_url:
            sellers.append(row_data)

    return sellers


def has_products(session: Session, seller_id: int) -> bool:
    params = {
        'appType': '1',
        'curr': 'rub',
        'dest': '123585494',
        'sort': 'popular',
        'spp': '30',
        'supplier': seller_id,
    }

    while True:
        response = session.get(
            'https://catalog.wb.ru/sellers/v4/catalog',
            params=params,
            headers=get_catalog_headers(seller_id),
            timeout=(3, 5)
        )

        if sleep_if_429(response, seller_id, 'запрос каталога'):
            continue

        break

    if response.status_code != 200:
        print(f'Продавец {seller_id}: статус каталога {response.status_code}')
        return False

    json_data = response.json()
    return bool(json_data.get('products', []))


def save_excel(data: list[dict], file_path: str) -> None:
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Sellers'

    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row.get(header) for header in headers])

    wb.save(file_path)
    print(f'Сохранено {len(data)} записей в {file_path}')


def filter_sellers_with_products() -> None:
    if not os.path.exists(SOURCE_FILE_PATH):
        print(f'Файл не найден: {SOURCE_FILE_PATH}')
        return

    sellers = load_sellers(SOURCE_FILE_PATH)
    result_list = []

    with Session() as session:
        for row_data in sellers:
            seller_url = row_data.get('Ссылка')
            seller_id = extract_seller_id(seller_url)
            if seller_id is None:
                print(f'Не удалось получить seller_id из ссылки: {seller_url}')
                continue

            try:
                time.sleep(randint(1, 3))
                if not has_products(session, seller_id):
                    print(f'Продавец {seller_id}: товаров нет')
                    continue

                result_list.append(row_data)
                print(f'Продавец {seller_id}: товары есть')
            except Exception as ex:
                print(f'{seller_url}: {ex}')
                continue

    save_excel(result_list, RESULT_FILE_PATH)


def main() -> None:
    filter_sellers_with_products()

    execution_time = datetime.now() - start_time
    print('Проверка товаров завершена.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
