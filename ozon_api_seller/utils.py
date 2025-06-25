import os
from datetime import datetime

import requests

import pandas as pd


def save_excel(data: list[dict], filename_prefix: str) -> None:
    """
    Сохраняет переданные данные в Excel-файл с текущей датой и временем в имени.
    """
    now_str = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"{filename_prefix}_{now_str}.xlsx"

    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f'✅ Данные сохранены в {filename}')


def save_csv(file_url: str, filename: str) -> None:
    """
    Сохраняет CSV по ссылке в указанный файл.
    """
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()

        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ CSV файл сохранён: {filename}')
    except requests.exceptions.RequestException as e:
        print(f'❌ Ошибка загрузки CSV: {e}')
    except IOError as e:
        print(f'❌ Ошибка сохранения CSV: {e}')


def prepare_excel_from_csv(csv_path: str, excel_path: str, column_mapping: dict, target_columns: list) -> None:
    """
    Загружает CSV, переименовывает колонки, добавляет отсутствующие целевые колонки,
    приводит некоторые колонки к строковому типу и сохраняет в Excel.

    :param csv_path: путь к исходному CSV-файлу
    :param excel_path: путь для сохранения Excel
    :param column_mapping: словарь {исходное_название: целевое_название}
    :param target_columns: список всех нужных столбцов целевой таблицы
    """
    df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')

    # Переименовываем колонки
    df.rename(columns=column_mapping, inplace=True)

    # Добавляем отсутствующие целевые колонки пустыми
    for col in target_columns:
        if col not in df.columns:
            df[col] = ''

    # Перемещаем колонки в нужном порядке (оставляя только нужные)
    df = df[target_columns]

    # Приводим некоторые столбцы к строковому типу, чтобы убрать кавычки в Excel
    str_columns = ['Артикул', 'SKU', 'Ozon SKU ID', 'Штрихкод', 'Barcode', 'Объем, л', 'Объемный вес, кг']
    for col in str_columns:
        if col in df.columns:
            # Убираем возможный ведущий апостроф и пробелы
            df[col] = df[col].astype(str).str.lstrip("'").str.strip()

    # Сохраняем в Excel без индексов
    df.to_excel(excel_path, index=False)
    print(f'✅ Excel сохранён в {excel_path}')
