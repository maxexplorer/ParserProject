import os
import time
from datetime import datetime, date

from requests import Session
from pandas import DataFrame, ExcelWriter

# =============================================================================
# Глобальные настройки
# =============================================================================

# Время старта программы (используется для подсчёта времени выполнения)
start_time: datetime = datetime.now()

# HTTP-заголовки для имитации запроса от браузера
headers: dict = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=1, i',
    'referer': 'https://www.propertyfinder.ae/en/buy/properties-for-sale.html',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'x-nextjs-data': '1',
}


# =============================================================================
# Работа с API PropertyFinder
# =============================================================================

def get_json(headers: dict, session: Session, page: int) -> dict | None:
    """
    Загружает JSON-данные выдачи PropertyFinder для указанной страницы.

    Используется Next.js endpoint, который возвращает
    структурированные данные по объявлениям.

    :param headers: HTTP-заголовки запроса
    :param session: Активная requests.Session
    :param page: Номер страницы выдачи
    :return: JSON-ответ в виде dict или None при ошибке
    """
    params: dict = {
        'page': page,
        'categorySlug': 'buy',
        'propertyTypeSlug': 'properties',
        'saleType': 'for-sale',
        'pattern': '/categorySlug/propertyTypeSlug-saleType.html',
    }

    try:
        response = session.get(
            'https://www.propertyfinder.ae/search/_next/data/j-QQFuo_Ac5zdYbWJhTfR/en/buy/properties-for-sale.html.json',
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


# =============================================================================
# Сбор и обработка данных
# =============================================================================

def get_data(headers: dict) -> list[dict[str, str | int | None]]:
    """
    Собирает объявления о продаже недвижимости с сайта PropertyFinder.

    В итоговую выборку попадают только объявления,
    опубликованные **сегодня (по UTC)**.

    :param headers: HTTP-заголовки запроса
    :return: Список словарей с данными объявлений
    """
    result_data: list[dict[str, str | int | None]] = []

    # Используем одну HTTP-сессию для всех запросов
    with Session() as session:

        pages: int = 3  # Количество страниц для обработки

        for page in range(1, pages + 1):
            try:
                # Пауза между запросами для снижения риска блокировки
                time.sleep(1)

                json_data: dict | None = get_json(
                    headers=headers,
                    session=session,
                    page=page
                )

            except Exception as ex:
                print(f'page {page}: {ex}')
                continue

            if not json_data:
                print('not json_data')
                continue

            # Извлечение списка объявлений
            items: list | None = (
                json_data
                .get('pageProps', {})
                .get('searchResult', {})
                .get('listings')
            )

            if not items:
                print('not items')
                continue

            for item in items:
                properties: dict | None = item.get('property')

                if not properties:
                    continue

                # -----------------------------------------------------------------
                # Дата публикации объявления (UTC)
                # -----------------------------------------------------------------
                listed_date: str | None = properties.get('listed_date')
                if not listed_date:
                    continue

                date_obj: datetime = datetime.strptime(
                    listed_date, '%Y-%m-%dT%H:%M:%SZ'
                )

                # Фильтрация: только объявления за сегодняшний день
                if date_obj.date() != date.today():
                    continue

                # -----------------------------------------------------------------
                # Основные данные объекта
                # -----------------------------------------------------------------
                property_id: int | None = properties.get('id')
                property_type: str | None = properties.get('property_type')
                title: str | None = properties.get('title')

                # Локация
                location: dict = properties.get('location', {})
                full_name: str | None = location.get('full_name')
                building_type: str | None = location.get('type')
                building_name: str | None = location.get('name')

                # Цена
                price_info: dict = properties.get('price', {})
                price: int | None = price_info.get('value')
                currency: str | None = price_info.get('currency')

                # Комнаты
                bedrooms: int | None = properties.get('bedrooms')
                bathrooms: int | None = properties.get('bathrooms')

                # Площадь
                size_info: dict = properties.get('size', {})
                size: int | None = size_info.get('value')
                unit: str | None = size_info.get('unit')

                # Дополнительная информация
                completion_status: str | None = properties.get('completion_status')
                description: str | None = properties.get('description')
                amenities: str = ', '.join(
                    properties.get('amenity_names', [])
                )
                property_url: str | None = properties.get('share_url')

                # Изображения
                image_urls: str = ', '.join(
                    image.get('medium')
                    for image in properties.get('images', [])
                    if image.get('medium')
                )

                # Брокер
                broker: dict = properties.get('broker') or {}
                broker_name: str | None = broker.get('name')
                broker_address: str | None = broker.get('address')
                broker_email: str | None = broker.get('email')
                broker_phone: str | None = broker.get('phone')

                # -----------------------------------------------------------------
                # Добавление результата
                # -----------------------------------------------------------------
                result_data.append(
                    {
                        'listed_date': date_obj,
                        'property_id': property_id,
                        'property_type': property_type,
                        'title': title,
                        'full_name': full_name,
                        'building_type': building_type,
                        'building_name': building_name,
                        'price': price,
                        'currency': currency,
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'size': size,
                        'size_unit': unit,
                        'completion_status': completion_status,
                        'description': description,
                        'amenities': amenities,
                        'property_url': property_url,
                        'image_urls': image_urls,
                        'broker_name': broker_name,
                        'broker_address': broker_address,
                        'broker_email': broker_email,
                        'broker_phone': broker_phone,
                    }
                )

            print(f'Обработано страниц: {page}/{pages}')

    return result_data


# =============================================================================
# Сохранение данных
# =============================================================================

def save_excel(data: list) -> None:
    """
    Сохраняет собранные данные в Excel-файл (.xlsx).

    Файл сохраняется в директорию `results`
    с текущей датой в названии.

    :param data: Список словарей с объявлениями
    """
    cur_date: str = datetime.now().strftime('%d-%m-%Y')
    directory: str = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path: str = f'{directory}/result_data_{cur_date}.xlsx'

    dataframe: DataFrame = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(
            writer,
            sheet_name='data',
            index=False
        )

    print(f'Данные сохранены в файл {file_path}')


# =============================================================================
# Точка входа
# =============================================================================

def main() -> None:
    """
    Точка входа в программу.

    Запускает сбор данных,
    сохраняет результат в Excel
    и выводит общее время выполнения.
    """
    try:
        result_data: list = get_data(headers=headers)
        save_excel(data=result_data)

    except Exception as ex:
        print(f'main: {ex}')
        input('Нажмите Enter, чтобы закрыть программу...')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершён!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
