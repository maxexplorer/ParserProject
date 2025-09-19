import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math

from requests import Session
import pandas as pd
from pandas import DataFrame, ExcelWriter, read_excel

from data.data import category_dict

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
    ]

    for low, high, basket in ranges:
        if low <= short_id <= high:
            return basket

    if short_id > 2189:
        return '15'

    print(f'Некорректный short_id: {short_id}')
    return None


def get_card_product(product_id: int, session: Session) -> str | None:
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
    }

    try:
        response = session.get(
            f'https://basket-{basket}.wbbasket.ru/vol{short_id}/part{product_id // 1000}/{product_id}/info/ru/card.json',
            headers=headers
        )
        if response.status_code != 200:
            print(f'colors: {product_id} status_code: {response.status_code}')
            return None

        json_data = response.json()
        options = json_data.get('options', [])

    except Exception as ex:
        print(f'{product_id}: {ex}')
        return None

    value = next(
        (opt.get('value') for opt in options if opt.get('name') == 'Объем скороварки'),
        None
    )
    return value


def aggregate_products(result_list, group_by_product=False, category_name=None):
    """
    Агрегирует данные по бренду (и по модели, если указано),
    добавляет колонку 'Товар' как категорию (без группировки).
    Дополнительные характеристики просто подтягиваются без агрегации.
    """
    df = pd.DataFrame(result_list)

    # Базовые агрегаты
    agg_dict = {
        'Min цена': ('Цена', 'min'),
        'Max цена': ('Цена', 'max'),
        'Медианная цена': ('Цена', median_mean),
        'Размер': ('Размер', lambda x: ', '.join(sorted(set(filter(None, x)))))
    }

    # Колонки для группировки
    group_cols = ['Бренд']
    if group_by_product and 'Модель' in df.columns:
        group_cols.append('Модель')

    # Агрегируем только то, что нужно
    result = df.groupby(group_cols).agg(**agg_dict).reset_index()

    # Добавляем колонку "Товар" (одно значение для всех строк категории)
    result['Товар'] = category_name if category_name else ''

    # Остальные дополнительные поля (без агрегации, просто добавляем если они есть)
    extra_fields = [
        'Объем накопителя',
        'Тип накопителя',
        'Емкость аккумулятора',
        'Мощность устройства',
        'Модель транспортного средства',
        'Модель спортивная',
        'Модель тренажера',
        'Объем скороварки'
    ]

    # Дополнительные поля добавляем только если есть Модель
    if 'Модель' in df.columns:
        for col in extra_fields:
            if col in df.columns and col != 'Модель':
                extras = df[['Модель', col]].drop_duplicates(subset=['Модель'])
                result = result.merge(extras, on='Модель', how='left')

    # Желаемый порядок колонок
    desired_order = [
        'Товар', 'Max цена', 'Min цена', 'Медианная цена', 'Бренд', 'Модель',
        'Объем накопителя', 'Тип накопителя', 'Емкость аккумулятора',
        'Мощность устройства', 'Модель транспортного средства',
        'Модель спортивная', 'Модель тренажера',
        'Размер', 'Объем скороварки'
    ]

    for col in desired_order:
        if col not in result.columns:
            result[col] = ''

    result = result[desired_order]
    return result


def median_mean(x, lower=0.1, upper=0.1):
    """
    Вычисляет среднее после усечения нижних и верхних процентов и округляет результат.

    :param x: Series с ценами
    :param lower: Процент для отсечения снизу
    :param upper: Процент для отсечения сверху
    :return: Округленное среднее значение
    """
    sorted_x = x.sort_values()
    n = len(sorted_x)
    lower_idx = int(n * lower)
    upper_idx = int(n * (1 - upper))
    truncated = sorted_x.iloc[lower_idx:upper_idx]
    value = truncated.mean() if len(truncated) > 0 else x.mean()
    return round(value)


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


def get_products_data(category_dict: dict, batch_size: int = 100) -> None:
    """
    Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel.

    :param category_dict: Словарь категорий и их URL
    :param batch_size: Количество товаров на страницу
    """
    with Session() as session:
        for category_name, category_url in category_dict.items():
            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': category_url,
                'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            }

            # Параметры запроса для первой страницы
            first_params = {
                'ab_testid': 'top_gmv',
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'lang': 'ru',
                'page': 1,
                'query': 'Гитара акустическая',
                'resultset': 'catalog',
                'sort': 'popular',
                'spp': '30',
                'suppressSpellcheck': 'false',
            }

            try:
                time.sleep(1)
                response = session.get(
                    'https://u-search.wb.ru/exactmatch/ru/common/v18/search',
                    params=first_params,
                    headers=headers,
                    timeout=(3, 5)
                )
                if response.status_code != 200:
                    print(f' category_url: {category_url}: статус ответа {response.status_code}')
                    continue

                json_data: dict = response.json()
                total = json_data.get('total', 0)
                if total == 0:
                    print(f"{category_name}: товаров нет")
                    continue

                pages = math.ceil(total / batch_size)
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
                    time.sleep(1)
                    response = session.get(
                        'https://u-search.wb.ru/exactmatch/ru/common/v18/search',
                        params=params,
                        headers=headers,
                        timeout=(3, 5)
                    )
                    if response.status_code != 200:
                        print(f' category_url: {category_url}: статус ответа {response.status_code}')
                        continue

                    json_data: dict = response.json()
                    data: list = json_data.get('products', [])

                except Exception as ex:
                    print(f"{category_name} страница {page}: {ex}")
                    continue

                if not data:
                    continue

                # Обрабатываем товары на странице
                for item in data:
                    brand = item.get('brand')
                    if brand is None or brand == '':
                        continue

                    product_id = item.get('id')
                    name = item.get('name')
                    size = item.get('sizes', [])[0].get('origName')
                    price = item.get('sizes', [])[0].get('price', {}).get('product') // 100

                    result_list.append(
                        {
                            'Бренд': brand,
                            'Цена': price,
                            'Размер': size,

                        }
                    )

                print(f'Обработано страниц: {page}/{pages}')

            # Агрегируем данные
            result = aggregate_products(result_list=result_list, category_name=category_name)

            # Сохраняем в Excel
            save_excel(result, category_name=category_name)

            print(f"{category_name}: данные сохранены, {len(result)} записей")


def main() -> None:
    """
    Точка входа в программу. Запускает обработку категорий и сбор данных о товарах.
    """
    get_products_data(category_dict=category_dict)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
