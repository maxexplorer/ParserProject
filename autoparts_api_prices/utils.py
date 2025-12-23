# utils.py

import os
from datetime import datetime

from pandas import DataFrame, ExcelWriter, read_excel


def load_article_info_from_excel(file_path: str) -> list[tuple[str, str]]:
    df = read_excel(file_path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=[df.columns[0], df.columns[1]])

    articles = []

    for row in df.itertuples(index=False):
        brand = str(row[0]).strip()
        article = str(row[1]).strip()
        articles.append((article, brand))

    return articles


def chunked(iterable, size=60):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def save_excel(data: list[dict], sheet_name: str = 'Лист1') -> None:
    """
    Сохраняет список словарей с данными о товарах в Excel-файл.

    Если файла нет — создает его.
    Если файл существует — дописывает новые данные в конец.

    Аргументы:
        data: Список словарей с данными товаров.
        category_name: Название категории для формирования имени файла.
    """

    cur_date = datetime.now().strftime('%d-%m-%Y')

    directory: str = 'results'
    file_path: str = f'{directory}/result_data_{cur_date}.xlsx'

    # Создаем директорию для результатов, если её нет
    os.makedirs(directory, exist_ok=True)

    # Если файла еще нет — создаем пустой Excel
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Читаем существующие данные
    df_existing: DataFrame = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows: int = len(df_existing.index)

    # Добавляем новые данные
    new_df: DataFrame = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows, header=(num_existing_rows == 0),
                        sheet_name=sheet_name, index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')
