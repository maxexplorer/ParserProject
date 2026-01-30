# avito_parser.py

import os
import time
from datetime import datetime, date, timedelta
import re
import math

from requests import Session

from pandas import DataFrame, ExcelWriter, read_excel

# =============================================================================
# Глобальные настройки
# =============================================================================

# Время старта программы (используется для подсчёта времени выполнения)
start_time: datetime = datetime.now()

# HTTP-заголовки для имитации запроса от браузера
headers: dict = {
    'accept': 'application/json',
    'referer': 'https://www.avito.ru/respublika_krym/zemelnye_uchastki?localPriority=0',
    'user-agent': 'Mozilla/5.0',
    'x-requested-with': 'XMLHttpRequest',
}


def get_build_id(session: Session, headers: dict) -> str | None:
    url = 'https://www.propertyfinder.ae/en/buy/properties-for-sale.html'
    r = session.get(url, headers=headers, timeout=30)

    if r.status_code != 200:
        return None

    match = re.search(r'"buildId":"([^"]+)"', r.text)
    return match.group(1) if match else None


# =============================================================================
# Работа с API Avito
# =============================================================================

def get_json(session: Session, headers: dict, page: int) -> dict | None:

    url = 'https://www.avito.ru/web/1/js/items'

    params = {
        'categoryId': '26',
        'locationId': '621550',
        'p': page,
        's': '104',
        'updateListOnly': 'true',
    }

    response = session.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f'status_code: {response.status_code}')
        return None

    return response.json()

def clean_text(text: str | None) -> str | None:
    if text is None:
        return None
    # Удаляем символы управления, оставляем только читаемые
    return re.sub(r'[\x00-\x1F\x7F]', ' ', text).strip()


def parse_date(timestamp: int | None) -> datetime | None:
    """Конвертирует timestamp (ms) в datetime"""
    if not timestamp:
        return None
    if timestamp > 1e10:  # миллисекунды
        timestamp /= 1000
    return datetime.fromtimestamp(timestamp)


# =============================================================================
# Сбор и обработка данных
# =============================================================================

def get_data(headers: dict, days: int = 1, batch_size: int = 100, limit: int = 50) -> list[dict[str, str | int | None]] | None:
    """
    Собирает объявления о продаже недвижимости с сайта PropertyFinder.

    :param headers: HTTP-заголовки запроса
    :param days: Количество дней назад (1 = только сегодня, 7 = неделя)
    :param batch_size: Количество записей для сохранения результата
    :param limit: Количество отображения карточек на странице
    :return: Список словарей с данными объявлений
    """

    result_data: list[dict[str, str | int | None]] = []

    # Граница по дате (UTC)
    today_utc: date = date.today()
    date_from: date = today_utc - timedelta(days=days - 1)

    max_consecutive_old = 3  # после 3 подряд старых объявлений выходим
    consecutive_old = 0  # общий счётчик по всем страницам

    # Используем одну HTTP-сессию для всех запросов
    with Session() as session:

        # Получаем первую страницу
        json_data: dict | None = get_json(session=session,
                            headers=headers,
                            page=1)

        if not json_data:
            print('first page not json_data')

        total = json_data.get('totalCount', 0)
        if total == 0:
            print(f"Карточек нет")
            return

        pages = math.ceil(total / limit)
        print(f"Всего {total} карточек, {pages} страниц")
        for page in range(1, pages + 1):
            try:
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

            items: list | None = (
                json_data
                .get('catalog', {})
                .get('items', [])

            )

            if not items:
                print('not items')
                continue

            for item in items:
                sort_ts = item.get('sortTimeStamp')
                date_obj = parse_date(sort_ts)

                if not date_obj:
                    continue

                listed_date_only: date = date_obj.date()

                # Проверка даты
                if not (date_from <= listed_date_only <= today_utc):
                    consecutive_old += 1
                    if consecutive_old >= max_consecutive_old:
                        return result_data  # выходим из get_data полностью
                    continue
                else:
                    consecutive_old = 0  # сброс счётчика, если дата подходит

                # -----------------------------------------------------------------
                # Основные данные объекта
                # -----------------------------------------------------------------
                property_id: int | None = item.get('id')
                property_type: str | None = item.get('category', {}).get('name')
                title: str | None = clean_text(item.get('title'))

                # Локация
                location: dict = item.get('coords', {}).get('address_user')

                # Цена
                price_info: dict = item.get('priceDetailed', {})
                price: int | None = price_info.get('value')
                normalized_price: str | None = price_info.get('normalizedPrice')

                # Дополнительная информация
                description: str | None = clean_text(item.get('description'))

                property_url: str | None = f"https://www.avito.ru{item.get('urlPath')}"


                # -----------------------------------------------------------------
                # Добавление результата
                # -----------------------------------------------------------------
                result_data.append(
                    {
                        'listed_date': date_obj,
                        'property_id': property_id,
                        'property_type': property_type,
                        'title': title,
                        'address': location,
                        'price': price,
                        'normalized_price': normalized_price,
                        'description': description,
                        'property_url': property_url
                    }
                )

            print(f'Обработано страниц: {page}/{pages}')

            # Сохраняем партию данных в Excel
            if len(result_data) >= batch_size:
                save_excel(result_data, 'Авито', today_utc)
                result_data.clear()

        # Сохраняем остаток
        if result_data:
            save_excel(result_data, 'Авито', today_utc)

    return result_data


# =============================================================================
# Сохранение данных
# =============================================================================
def save_excel(data: list[dict], source: str, today_utc: date) -> None:
    """
    Сохраняет список данных в Excel-файл (results/result_data.xlsx).

    :param data: Список словарей с данными о товарах.
    """
    cur_date: str = today_utc.strftime('%d-%m-%Y')

    directory = 'results'
    file_path = f'{directory}/result_data_{source}_{cur_date}.xlsx'

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

    days_to_collect: int = 1  # 1 = сегодня, 7 = неделя
    batch_size = 100

    try:
        result_data: list = get_data(headers=headers, days=days_to_collect, batch_size=batch_size)

    except Exception as ex:
        print(f'main: {ex}')
        input('Нажмите Enter, чтобы закрыть программу...')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершён!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
