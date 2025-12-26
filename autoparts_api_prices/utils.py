# utils.py

"""
Вспомогательные функции:
- загрузка данных из Excel
- разбиение списков на батчи
- сохранение результатов в Excel
"""

import os
from datetime import datetime

from pandas import DataFrame, ExcelWriter, read_excel


def load_article_info_from_excel(file_path: str) -> list[tuple[str, str]]:
    """
    Загружает артикулы и бренды из Excel.

    Ожидается:
    - 1 колонка — бренд
    - 2 колонка — артикул

    :param file_path: Путь к Excel-файлу
    :return: Список кортежей (article, brand)
    """

    df = read_excel(file_path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=[df.columns[0], df.columns[1]])

    articles: list = []

    for row in df.itertuples(index=False):
        brand: str = str(row[0]).strip()
        article: str = str(row[1]).strip()
        articles.append((article, brand))

    return articles


def chunked(iterable, size=60):
    """
    Делит список на части фиксированного размера.

    :param iterable: Исходный список
    :param size: Размер батча
    """
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def save_excel(data: list[dict], brand: str, sheet_name: str = 'Лист1') -> None:
    """
    Сохраняет данные в Excel-файл.

    - Если файл не существует — создает
    - Если существует — дописывает данные в конец

    :param data: Список словарей с данными
    :param sheet_name: Имя листа Excel
    """

    cur_date: str = datetime.now().strftime('%d-%m-%Y')

    directory: str = 'results'
    file_path: str = f'{directory}/result_data_{brand}_{cur_date}.xlsx'

    # Создаем директорию для результатов
    os.makedirs(directory, exist_ok=True)

    # Если файл отсутствует — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Читаем существующие данные
    df_existing: DataFrame = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows: int = len(df_existing.index)

    # Добавляем новые строки
    new_df: DataFrame = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows,
            header=(num_existing_rows == 0),
            sheet_name=sheet_name,
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')
