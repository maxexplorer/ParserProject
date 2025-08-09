import os
from datetime import datetime

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()


def get_inn(session: Session, headers: dict, seller_id: int) -> str | None:
    """
    Получает ИНН продавца по его ID через статичный JSON-эндпоинт WB.

    :param session: Активная сессия requests
    :param headers: Заголовки HTTP-запроса
    :param seller_id: ID продавца (строка)
    :return: ИНН как строка или None, если не найден
    """
    try:
        response = session.get(
            f'https://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/{seller_id}.json',
            headers=headers
        )
        json_data = response.json()
        inn = json_data.get('inn')
        return inn
    except Exception as ex:
        print(f'Ошибка при получении ИНН для {seller_id}: {ex}')
        return None


def get_registration_date_and_inn(session: Session, headers: dict, url: str, seller_id: int) -> tuple[str, str] | None:
    """
    Получает дату регистрации и общее количество продаж продавца.
    Проверяет, является ли продавец активным согласно условиям.

    :param session: Активная HTTP-сессия
    :param headers: Заголовки запроса
    :param seller_id: ID продавца
    :return: Кортеж (ссылка на продавца, ИНН) или None, если продавец неактивен или ошибка
    """

    try:
        response = session.get(
            f'https://suppliers-shipment-2.wildberries.ru/api/v1/suppliers/{seller_id}',
            headers=headers,
            timeout=60
        )
        json_data = response.json()
    except Exception as ex:
        print(f'Ошибка при получении данных о регистрации для {seller_id}: {ex}')
        return None

    registration_date = json_data.get('registrationDate')
    sale_item_quantity = json_data.get('saleItemQuantity')

    if registration_date and sale_item_quantity is not None:
        reg_date = datetime.strptime(registration_date, '%Y-%m-%dT%H:%M:%SZ')
        years_on_wb = (datetime.now() - reg_date).days // 365

        # Проверка условий "активности"
        if (
                (years_on_wb == 1 and sale_item_quantity >= 1000) or
                (years_on_wb == 2 and sale_item_quantity >= 4001) or
                (years_on_wb >= 3 and sale_item_quantity >= 9001)
        ):
            inn = get_inn(session, headers, seller_id)
            return url, inn

        return None


def process_sellers_range(start_id: int, end_id: int, batch_size: int = 100) -> None:
    """
    Обрабатывает продавцов в заданном диапазоне ID.
    Проверяет, активен ли продавец, и сохраняет данные в Excel.

    :param start_id: Начальный ID (включительно)
    :param end_id: Конечный ID (включительно)
    :param batch_size: Размер пакета для записи в Excel
    """

    result_list = []
    processed_count = 0

    with Session() as session:
        for seller_id in range(start_id, end_id + 1):
            url = f'https://www.wildberries.ru/seller/{seller_id}'

            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': f'https://www.wildberries.ru/seller/{seller_id}',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'x-client-name': 'site',
            }

            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '123585494',
                'sort': 'popular',
                'spp': '30',
                'supplier': seller_id,
            }

            try:
                response = session.get(
                    'https://catalog.wb.ru/sellers/v2/catalog',
                    params=params,
                    headers=headers,
                    timeout=60
                )

                if response.status_code != 200:
                    print(f'Продавец {seller_id}: статус ответа {response.status_code}')
                    continue

                json_data = response.json()
                data_products = json_data.get('data', {}).get('products', [])
                if not data_products:
                    continue

                result = get_registration_date_and_inn(session, headers, url, seller_id)

                if result:
                    result_list.append(
                        {
                            'Ссылка': result[0],
                            'ИНН': result[1]
                        }
                    )

            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            processed_count += 1
            print(f'Обработано продавцов: {processed_count}')

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
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    df_existing = read_excel(file_path, sheet_name='Sellers')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Sellers', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main() -> None:
    """
    Точка входа в программу. Запускает обработку продавцов в заданном диапазоне.
    """
    # Укажи нужный диапазон ID
    start_id = 1
    end_id = 5_000_000

    process_sellers_range(start_id, end_id)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
