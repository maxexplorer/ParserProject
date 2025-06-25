import os
from datetime import datetime
from io import StringIO

import pandas as pd
from openpyxl import load_workbook

from data.data import COLUMN_MAPPING, TARGET_COLUMNS


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


def save_to_excel_template(df: pd.DataFrame, template_path: str, output_path: str,
                           sheet_name: str = 'Товары и цены') -> None:
    """
    Записывает DataFrame в шаблон Excel, начиная с 5-й строки, не изменяя первые 4 строки.

    :param df: DataFrame с данными
    :param template_path: путь к шаблону Excel
    :param output_path: путь для сохранения итогового файла
    :param sheet_name: имя листа, куда вставить данные
    """
    # Создаём папку для сохранения при необходимости
    folder = os.path.dirname(output_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    # Загружаем шаблон
    wb = load_workbook(template_path)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f'❌ В шаблоне отсутствует лист "{sheet_name}"')

    ws = wb[sheet_name]

    # Пишем данные начиная с 5-й строки
    start_row = 5
    for row_idx, row in enumerate(df.itertuples(index=False), start=start_row):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(output_path)
    print(f'✅ Excel сохранён по шаблону: {output_path}')


def process_and_save_excel_from_csv_content(csv_content: str) -> None:
    df = pd.read_csv(StringIO(csv_content), delimiter=';')

    # Переименовываем колонки
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # Добавляем отсутствующие целевые колонки пустыми
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ''

    # Копируем цену
    price_col = 'Текущая цена (со скидкой), руб.'
    min_price_col = 'Минимальная цена, руб.'
    if price_col in df.columns:
        df[min_price_col] = df[price_col]

    # Оставляем только нужные колонки и в нужном порядке
    df = df[TARGET_COLUMNS]

    # Приводим некоторые колонки к строковому типу
    str_columns = ['Артикул', 'SKU', 'Ozon SKU ID', 'Штрихкод', 'Barcode', 'Объем, л', 'Объемный вес, кг']
    for col in str_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lstrip("'").str.strip()

    # Сохраняем в шаблон
    template_path = 'data/Шаблон цен.xlsx'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_path = f'results/ozon_products_{timestamp}.xlsx'

    save_to_excel_template(df, template_path, output_path, sheet_name='Товары и цены')
