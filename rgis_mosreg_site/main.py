import os
import time
from datetime import datetime

from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

# Отметка времени начала работы программы
start_time = datetime.now()

# HTTP-заголовки для имитации запроса от браузера
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=1, i',
    'referer': 'https://rgis.mosreg.ru/v3/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}


def get_object_id(headers: dict) -> None:
    """
    Собирает список ID объектов из RGIS Mosreg.

    Для каждой страницы сайта формируется HTTP-запрос к API.
    Из JSON-ответа извлекаются ID карточек объектов недвижимости.

    Полученные ID сохраняются в файл 'data/id_list.txt'.

    :param headers: HTTP-заголовки для имитации запроса от браузера
    """
    object_ids = []
    pages = 38  # Количество страниц для обработки

    # Создаем сессию для всех запросов
    with Session() as session:
        for page in range(1, pages + 1):
            try:
                # Пауза между запросами, чтобы снизить риск блокировки
                time.sleep(1)

                cookies = {
                    '_ym_uid': '1768216732369099442',
                    '_ym_d': '1768216732',
                    '_ym_isad': '2',
                    'mojo': 'ВАША_АКТУАЛЬНАЯ_СЕССИЯ',
                }

                params = {
                    'id': '714',
                    'page': page,
                    'show': '100',
                }

                response = session.get(
                    'https://rgis.mosreg.ru/v3/swagger/geoportal/docs/list',
                    params=params,
                    cookies=cookies,
                    headers=headers
                )

                json_data = response.json()

            except Exception as ex:
                print(f'page {page}: {ex}')
                continue

            if not json_data:
                print('not json_data')
                continue

            # Извлекаем ID объектов из ответа
            for item in json_data:
                object_id = item.get('meta', {}).get('card')
                if object_id:
                    object_ids.append(object_id)

            print(f'Обработано страниц: {page}/{pages}')

    # Создаем папку data, если её нет
    os.makedirs('data', exist_ok=True)

    # Сохраняем ID объектов в файл
    with open('data/id_list.txt', 'a', encoding='utf-8') as file:
        print(*object_ids, file=file, sep='\n')


def get_data(file_path: str, headers: dict) -> None:
    """
    Собирает детальные данные о строительных объектах из RGIS Mosreg.

    Для каждого ID объекта выполняется запрос к API.
    Данные собираются в словари с ключами, соответствующими названиям полей из JSON.

    Пакеты данных по 100 объектов сохраняются в Excel для удобства.
    Остатки также сохраняются после обработки всех объектов.

    :param file_path: путь к файлу с ID объектов
    :param headers: HTTP-заголовки для имитации запроса от браузера
    """
    # Читаем ID объектов из файла
    with open(file_path, 'r', encoding='utf-8') as file:
        object_ids = [line.strip() for line in file.readlines()]

    result_data = []
    batch_size = 100  # Размер пакета для сохранения в Excel
    count_objects = len(object_ids)

    cookies = {
        '_ym_uid': '1768216732369099442',
        '_ym_d': '1768216732',
        '_ym_isad': '2',
        'mojo': 'eyJzZXNzaW9uX2lkIjoiZWRlODgwZTU5NjBhM2U2YWE2MmVjMGFmMDQzNDNmZDMiLCJleHBpcmVzIjoxNzY4MjMwNzIxLCJmIjoiUGpORXF2aGJvNXUvakdLSDBuYU9YMFJjb0pVPSJ9--38465e8edc4c155e344e8495361c898d31e7f512',
    }

    with Session() as session:
        for i, object_id in enumerate(object_ids, 1):
            params = {'id': object_id}

            try:
                # Пауза между запросами
                time.sleep(1)
                response = session.get(
                    'https://rgis.mosreg.ru/v3/swagger/geoportal/card/main',
                    params=params,
                    cookies=cookies,
                    headers=headers
                )
                json_data = response.json()
            except Exception as ex:
                print(f'object_id {object_id}: {ex}')
                continue

            if not json_data:
                print('not json_data')
                continue

            # json_data — список объектов с 'header' и 'content'
            item_dict = {}

            for section in json_data:
                header = section.get('header')  # например, "Строящийся объект"
                content = section.get('content', [])

                # Можно добавить header как отдельное поле
                item_dict['header'] = header

                # Проходим по всем полям в content
                for field in content:
                    key = field.get('title')
                    value = field.get('value')
                    item_dict[key] = value

            result_data.append(item_dict)
            print(f'Обработано объектов: {i}/{count_objects}')

            # Сохраняем пакет данных в Excel
            if len(result_data) >= batch_size:
                save_excel(result_data, 'result_data.xlsx')
                result_data.clear()

    # Сохраняем оставшиеся данные
    if result_data:
        save_excel(result_data, 'result_data.xlsx')


def save_excel(data: list[dict], file_name: str) -> None:
    """
    Сохраняет список словарей в Excel-файл.

    Если файл уже существует — дописывает новые строки в конец.
    Создает папку 'results', если её нет.

    :param data: список словарей с данными
    :param file_name: имя Excel-файла
    """
    directory = 'results'
    file_path = f'{directory}/{file_name}'

    # Создаем папку results, если нет
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


def main() -> None:
    """
    Точка входа в программу.

    Запускает сбор ID объектов, сбор детальных данных,
    сохраняет результат в Excel и выводит общее время работы.
    """
    try:
        # Сбор ID объектов
        # get_object_id(headers=headers)

        # Сбор данных по объектам
        get_data(file_path='data/id_list.txt', headers=headers)

    except Exception as ex:
        print(f'main: {ex}')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершён!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
