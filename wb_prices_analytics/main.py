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
    short_id = product_id // 100000

    # таблица диапазонов: (нижняя_граница, верхняя_граница, basket)
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


def aggregate_products(result_list, group_by_product=False):
    df = pd.DataFrame(result_list)

    # базовые агрегации
    agg_dict = {
        'Min цена': ('Цена', 'min'),
        'Max цена': ('Цена', 'max'),
        'Медианная цена': ('Цена', median_mean),
        'Размер': ('Размер', lambda x: ', '.join(sorted(set(filter(None, x)))))
    }

    # дополнительные поля
    extra_fields = [
        'Модель',
        'Объем накопителя',
        'Тип накопителя',
        'Емкость аккумулятора',
        'Мощность устройства',
        'Модель транспортного средства',
        'Модель спортивная',
        'Модель тренажера',
        'Объем скороварки'
    ]

    for col in extra_fields:
        if col in df.columns:
            agg_dict[col] = (col, lambda x: ', '.join(sorted(set(filter(None, x)))))

    # выбираем колонки для группировки
    group_cols = ['Бренд']
    if group_by_product:
        group_cols.append('Товар')

    result = df.groupby(group_cols).agg(**agg_dict).reset_index()

    # желаемый порядок колонок
    desired_order = [
        'Товар', 'Max цена', 'Min цена', 'Медианная цена', 'Бренд', 'Модель',
        'Объем накопителя', 'Тип накопителя', 'Емкость аккумулятора',
        'Мощность устройства', 'Модель транспортного средства',
        'Модель спортивная', 'Модель тренажера',
        'Размер', 'Объем скороварки'
    ]

    # добавляем отсутствующие колонки пустыми
    for col in desired_order:
        if col not in result.columns:
            result[col] = ''

    result = result[desired_order]

    return result


def median_mean(x, lower=0.1, upper=0.1):
    """Вычисляет среднее после усечения нижних и верхних процентов и округляет результат."""
    sorted_x = x.sort_values()
    n = len(sorted_x)
    lower_idx = int(n * lower)
    upper_idx = int(n * (1 - upper))
    truncated = sorted_x.iloc[lower_idx:upper_idx]
    value = truncated.mean() if len(truncated) > 0 else x.mean()
    return round(value)



def save_excel(data: list[dict], category_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data_{category_name}.xlsx'

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


def get_products_data(category_dict: dict, batch_size: int = 100) -> None:
    """Собирает данные о товарах по категориям и сохраняет min/max/median цены в Excel"""
    with Session() as session:
        for category_name, category_url in category_dict.items():
            # parsed_url = urlparse(category_url)
            # params_qs = parse_qs(parsed_url.query)
            # xsubject = params_qs.get("xsubject", [None])[0]

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

            # первый запрос для получения total
            first_params = {
                'ab_testid': 'top_gmv',
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'lang': 'ru',
                'page': 1,
                'query': 'Контейнер для еды с подогревом',
                'resultset': 'catalog',
                'sort': 'popular',
                'spp': '30',
                'suppressSpellcheck': 'false',
                # 'xsubject': xsubject,
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

            # проходим по всем страницам
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

                for item in data:
                    item: dict

                    brand = item.get('brand')

                    if brand is None or brand == '':
                        continue

                    product_id = item.get('id')

                    name = item.get('name')

                    size = item.get('sizes', [])[0].get('origName')

                    price = item.get('sizes', [])[0].get('price', {}).get('product') // 100

                    # option_value = get_card_product(product_id=product_id, session=session)

                    result_list.append(
                        {
                            'Товар': name,
                            'Бренд': brand,
                            'Размер': size,
                            'Цена': price,
                        }
                    )

                print(f'Обработано страниц: {page}/{pages}')

            result = aggregate_products(result_list=result_list)

            save_excel(result, category_name=category_name)

            print(f"{category_name}: данные сохранены, {len(result)} записей")


def main() -> None:
    """
    Точка входа в программу. Запускает обработку продавцов в заданном диапазоне.
    """

    get_products_data(category_dict=category_dict)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
