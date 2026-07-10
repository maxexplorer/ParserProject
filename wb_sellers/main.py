import os
import time
from datetime import datetime
from random import randint

from requests import Response, Session
from openpyxl import Workbook, load_workbook

start_time = datetime.now()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
DEFAULT_429_PAUSE = 5


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


def is_active_seller(years_on_wb: int, sale_item_quantity: int) -> bool:
    if years_on_wb == 0:
        return sale_item_quantity >= 2000
    if years_on_wb == 1:
        return sale_item_quantity >= 4000
    if years_on_wb == 2:
        return sale_item_quantity >= 8000

    return sale_item_quantity >= 15000


def get_inn(session: Session, seller_id: int) -> str | None:
    """
    Получает ИНН продавца по его ID через статичный JSON-эндпоинт WB.

    :param session: Активная сессия requests
    :param seller_id: ID продавца (строка)
    :return: ИНН как строка или None, если не найден
    """
    for _ in range(3):
        try:
            response = session.get(
                f'https://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/{seller_id}.json',
                headers=get_api_headers(seller_id),
                timeout=(3, 5)
            )

            if sleep_if_429(response, seller_id, 'запрос ИНН'):
                continue

            if response.status_code != 200:
                print(f'Продавец {seller_id}: статус ИНН {response.status_code}')
                return None

            json_data = response.json()
            inn = json_data.get('inn')
            return inn
        except Exception as ex:
            print(f'Ошибка при получении ИНН для {seller_id}: {ex}')
            time.sleep(DEFAULT_429_PAUSE)

    return None


def get_registration_date_and_inn(session: Session, seller_id: int) -> str | None:
    """
    Получает дату регистрации и общее количество продаж продавца.
    Проверяет, является ли продавец активным согласно условиям.

    :param session: Активная HTTP-сессия
    :param seller_id: ID продавца
    :return: ИНН или None, если продавец неактивен или ошибка
    """
    try:
        response = session.get(
            f'https://suppliers-shipment-2.wildberries.ru/api/v1/suppliers/{seller_id}',
            headers=get_api_headers(seller_id),
            timeout=(3, 5)
        )

        if response.status_code != 200:
            print(f'Продавец {seller_id}: статус статистики {response.status_code}')
            return None

        json_data = response.json()
    except Exception as ex:
        print(f'Ошибка при получении данных о регистрации для {seller_id}: {ex}')
        return None

    registration_date = json_data.get('registrationDate')
    sale_item_quantity = json_data.get('saleItemQuantity')

    if registration_date and sale_item_quantity is not None:
        reg_date = datetime.strptime(registration_date, '%Y-%m-%dT%H:%M:%SZ')
        years_on_wb = (datetime.now() - reg_date).days // 365

        if is_active_seller(years_on_wb, sale_item_quantity):
            return get_inn(session, seller_id)

        return None

    return None


def process_sellers_range(start_id: int, end_id: int, batch_size: int = 50) -> None:
    """
    Обрабатывает продавцов в заданном диапазоне ID.
    Проверяет, активен ли продавец, и сохраняет данные в Excel.

    :param start_id: Начальный ID (включительно)
    :param end_id: Конечный ID (включительно)
    :param batch_size: Размер пакета для записи в Excel
    """

    result_list = []

    with Session() as session:
        for seller_id in range(start_id, end_id + 1):
            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '123585494',
                'sort': 'popular',
                'spp': '30',
                'supplier': seller_id,
            }

            try:
                while True:
                    time.sleep(randint(1, 3))
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
                    print(f'Продавец {seller_id}: статус ответа {response.status_code}')
                    continue

                json_data = response.json()
                data_products = json_data.get('products', [])
                if not data_products:
                    print(f'Обработан продавец ID: {seller_id}')
                    continue

                inn = get_registration_date_and_inn(session, seller_id)

                if inn is None:
                    print(f'Обработан продавец ID: {seller_id}')
                    continue

                result_list.append(
                    {
                        'Ссылка': f'https://www.wildberries.ru/seller/{seller_id}',
                        'ИНН': inn
                    }
                )
                print(f'Обработан продавец ID: {seller_id}, inn: {inn}')

            except Exception as ex:
                print(f'https://www.wildberries.ru/seller/{seller_id}: {ex}')
                continue

            if len(result_list) >= batch_size:
                save_excel(result_list)
                result_list.clear()

    if result_list:
        save_excel(result_list)


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data_4_000_000.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Sellers'
        ws.append(list(data[0].keys()))
    else:
        wb = load_workbook(file_path)
        ws = wb['Sellers'] if 'Sellers' in wb.sheetnames else wb.active

        if ws.max_row == 1 and all(cell.value is None for cell in ws[1]):
            ws.append(list(data[0].keys()))

    excel_headers = [cell.value for cell in ws[1]]
    for row in data:
        ws.append([row.get(header) for header in excel_headers])

    wb.save(file_path)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main() -> None:
    """
    Точка входа в программу. Запускает обработку продавцов в заданном диапазоне.
    """
    # Укажи нужный диапазон ID
    start_id = 4_011_731
    end_id = 4_300_000

    process_sellers_range(start_id, end_id)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
