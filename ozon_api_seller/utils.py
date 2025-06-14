import os
import glob

import pandas as pd

def load_article_prices_from_excel(folder: str = 'data') -> dict:
    """
    Загружает артикулы и цены из первого найденного Excel-файла в папке `folder`.
    Возвращает словарь вида {артикул: цена}.
    """
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    path = excel_files[0]
    print(f'📄 Загружаю Excel: {path}')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Артикул', df.columns[2]])

    return {
        str(row['Артикул']).strip(): row.iloc[2]
        for _, row in df.iterrows()
    }