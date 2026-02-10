# utils.py

"""
Вспомогательные функции:
- загрузка данных из Excel
- разбиение списков на батчи
- сохранение результатов в Excel
"""

import os
import glob
from datetime import datetime, timedelta

from pandas import DataFrame, ExcelWriter, read_excel

import unicodedata

SHEET_INDEX_BY_FILENAME = {
    'прайс.xls': 1, # Прайс.xls → берём 2-й лист (index=1)
}


def load_articles_from_data(folder: str = 'data') -> dict:
    """
    Загружает артикулы и бренды из первого найденного Excel в папке data.
    Возвращает словарь с ключами SAT, OEM, OTHER
    """
    files = glob.glob(os.path.join(folder, '*.xls*'))
    if not files:
        print('❗ В папке data/ нет Excel-файлов (.xls или .xlsx)')
        return {}

    # Берем первый файл
    file_path = files[0]
    df = read_excel(file_path)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=[df.columns[0], df.columns[1]])

    sat_list, oem_list, other_list = [], [], []

    for row in df.itertuples(index=False):
        brand = str(row[0]).strip()
        article = str(row[1]).strip()
        if brand.upper() == "SAT":
            sat_list.append((article, brand))
        elif brand.upper() == "OEM":
            oem_list.append((article, brand))
        else:
            other_list.append((article, brand))

    print(f"Загружено: SAT={len(sat_list)}, OEM={len(oem_list)}, OTHER={len(other_list)} артикулов")
    return {"SAT": sat_list, "OEM": oem_list, "OTHER": other_list}


def load_prices_from_file(
        file_path: str,
        col_article: int,
        col_price: int
) -> list[dict]:
    """
       Универсальная функция для загрузки прайса из Excel-файла.
       Автоматически пропускает строки, где не удается распарсить артикул или цену.
       Можно сразу фильтровать только нужные артикулы (allowed_articles).

       :param file_path: путь к Excel
       :param col_article: индекс колонки с артикулом (0-based)
       :param col_price: индекс колонки с ценой (0-based)
       :return: список словарей {'Артикул': article, 'Цена': price, 'Источник': file_name}
       """
    try:
        sheet_index = get_sheet_index(file_path)

        df = read_excel(
            file_path,
            header=None,
            sheet_name=sheet_index
        )

    except Exception as ex:
        print(f"❌ Ошибка чтения файла {file_path}: {ex}")
        return []

    result = []

    for row in df.itertuples(index=False):
        try:
            article = str(row[col_article]).strip()
            price_str = str(row[col_price]).replace(',', '.')
            price = float(''.join(filter(lambda c: c.isdigit() or c == '.', price_str)))

            if article and price > 0:
                result.append({
                    'Артикул': article,
                    'Цена': price,
                    'Источник': os.path.basename(file_path)
                })
        except Exception:
            continue

    print(f"📦 Обработан файл: {os.path.basename(file_path)}, записей: {len(result)}")
    return result


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text.lower())


def get_sheet_index(file_path: str) -> int:
    filename = normalize(os.path.basename(file_path))

    return SHEET_INDEX_BY_FILENAME.get(filename, 0)


def chunked(iterable, size=60):
    """
    Делит список на части фиксированного размера.

    :param iterable: Исходный список
    :param size: Размер батча
    """
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


def remove_yesterday_file() -> None:
    """
    Удаляет файл Excel с результатами за вчерашний день
    в соответствии с save_excel().
    """

    directory = 'results'
    os.makedirs(directory, exist_ok=True)

    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%d-%m-%Y')

    filename = f'result_data_{date_str}.xlsx'
    filepath = os.path.join(directory, filename)

    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"[OK] Удалён файл: {filepath}")
    else:
        print(f"[INFO] Файл не найден: {filepath}")


def clear_prices_folder(folder: str = 'prices'):
    """Удаляет все файлы Excel в папке prices"""
    files = glob.glob(os.path.join(folder, '*.xls')) + glob.glob(os.path.join(folder, '*.xlsx'))
    for f in files:
        try:
            os.remove(f)
        except Exception:
            continue


def save_excel(data: list[dict], directory: str = 'results', file_name: str = 'result_data',
               sheet_name: str = 'Лист1') -> None:
    """
    Сохраняет данные в Excel-файл.

    - Если файл не существует — создает
    - Если существует — дописывает данные в конец

    :param data: Список словарей с данными
    :param directory: Имя директории
    :param file_name: Имя файла
    :param sheet_name: Имя листа Excel
    """

    cur_date: str = datetime.now().strftime('%d-%m-%Y')

    file_path: str = f'{directory}/{file_name}_{cur_date}.xlsx'

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
