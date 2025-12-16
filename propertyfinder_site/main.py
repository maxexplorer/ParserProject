import os
import time
from datetime import datetime

from requests import Session
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

headers = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=1, i',
    'referer': 'https://www.propertyfinder.ae/en/buy/properties-for-sale.html?page=1',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'x-nextjs-data': '1',
}


def get_json(headers: dict, session: Session, page: int) -> dict | None:
    """
    Получить JSON с новостями с указанной страницы.

    :param headers: Заголовки HTTP запроса
    :param session: Объект requests.Session для повторного использования соединения
    :param page: Номер страницы для запроса
    :return: JSON-ответ в виде словаря или None в случае ошибки
    """
    params = {
        'page': page,
        'categorySlug': 'buy',
        'propertyTypeSlug': 'properties',
        'saleType': 'for-sale',
        'pattern': '/categorySlug/propertyTypeSlug-saleType.html',
    }
    try:
        response = session.get(
            'https://www.propertyfinder.ae/search/_next/data/2uummsZcqGe1HZV7ZIrBW/en/buy/properties-for-sale.html.json',
            params=params,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')
            return None

        return response.json()
    except Exception as ex:
        print(f'get_json: {ex}')
        return None


def get_data(headers: dict) -> list[dict[str, str | int | None]]:
    """
    Собирает данные статей с сайта, фильтруя по ключевому слову 'ТиНАО'.

    :param headers: Заголовки HTTP запроса
    :return: Список словарей с информацией по статьям
    """
    result_data = []

    with Session() as session:

        pages = 3

        for page in range(1, pages + 1):
            try:
                time.sleep(1)  # Пауза между запросами, чтобы избежать блокировки
                # Получаем JSON данные для каждой страницы
                json_data = get_json(headers=headers, session=session, page=page)
            except Exception as ex:
                print(f"page: {page} - {ex}")
                continue

            if not json_data:
                print('not json_data')
                continue

            data = json_data.get('pageProps', {}).get('searchResult', {}).get('listings')

            if not data:
                print('not data')
                continue

            for item in data:
                properties = item.get('property')

                if properties is None:
                    continue

                listed_date = properties.get('listed_date')
                date = datetime.strptime(listed_date, '%Y-%m-%dT%H:%M:%SZ')

                property_id = properties.get('id')

                property_type = properties.get('property_type')

                title = properties.get('title')

                price = properties.get('price', {}).get('value')

                currency = properties.get('price', {}).get('currency')

                location = properties.get('location', {}).get('full_name')

                building_type = properties.get('location', {}).get('type')

                images = ', '.join(i.get('medium') for i in properties.get('images', []))

                broker_items = properties.get('broker')
                broker_name = broker_items.get('name')
                broker_address = broker_items.get('address')
                broker_email = broker_items.get('email')
                broker_phone = broker_items.get('phone')

                size = properties.get('size', {}).get('value')
                unit = properties.get('size', {}).get('unit')

                property_url = properties.get('share_url')

                completion_status = properties.get('completion_status')

                description = properties.get('description')

                amenities = ', '.join(c for c in properties.get('amenity_names', []))

                result_data.append(
                    {
                        'listed_date': date,
                        'property_id': property_id,
                        'property_type': property_type,
                        'title': title,
                        'price': price,
                        'currency': currency,
                        'location': location,
                        'building_type': building_type,
                        'images': images,
                        'broker_name': broker_name,
                        'broker_address': broker_address,
                        'broker_email': broker_email,
                        'broker_phone': broker_phone,
                        'size': size,
                        'size_unit': unit,
                        'property_url': property_url,
                        'completion_status': completion_status,
                        'description': description,
                        'amenities': amenities,
                    }
                )

            print(f'Обработано: {page}/{pages}')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    cur_date = datetime.now().strftime('%d-%m-%Y')

    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{cur_date}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main() -> None:
    """
    Основная функция запуска скрипта.
    Собирает данные и сохраняет их в Excel.
    """
    try:
        result_data = get_data(headers=headers)

        save_excel(data=result_data)

    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
