# utils.py
"""
Вспомогательные функции проекта.

Модуль отвечает за:
- загрузку артикулов из Excel (data/)
- загрузку цен из прайсов (prices/)
- выбор нужного листа Excel (в т.ч. для файлов-исключений)
- сохранение результатов в Excel
- утилитарные операции (нормализация, батчинг, очистка)
"""

import os
import glob
from datetime import datetime, timedelta

from pandas import DataFrame, ExcelWriter, read_excel
import unicodedata


# ---------------------------------------------------------------------
# Конфигурация листов Excel
# ---------------------------------------------------------------------

# Маппинг: имя файла → индекс листа с данными
# Используется, если в файле есть служебный (скрытый) лист,
# который необходимо пропустить.
SHEET_INDEX_BY_FILENAME = {
    'прайс.xls': 1,  # Прайс.xls → данные находятся на 2-м листе
}


# ---------------------------------------------------------------------
# Загрузка артикулов из data/
# ---------------------------------------------------------------------

def load_articles_from_data(folder: str = 'data') -> dict:
    """
    Загружает артикулы и бренды из первого Excel-файла в папке data/.

    Ожидаемая структура файла:
    - колонка 0: бренд
    - колонка 1: артикул

    Возвращает словарь:
    {
        "SAT":   [(article, brand), ...],
        "OEM":   [(article, brand), ...],
        "OTHER": [(article, brand), ...]
    }
    """

    files = glob.glob(os.path.join(folder, '*.xls*'))
    if not files:
        print('❗ В папке data/ нет Excel-файлов (.xls или .xlsx)')
        return {}

    # Используем первый найденный файл
    file_path = files[0]

    df = read_excel(file_path)
    df.columns = df.columns.str.strip()

    # Убираем строки без бренда или артикула
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

    print(
        f"Загружено: SAT={len(sat_list)}, "
        f"OEM={len(oem_list)}, "
        f"OTHER={len(other_list)} артикулов"
    )

    return {
        "SAT": sat_list,
        "OEM": oem_list,
        "OTHER": other_list
    }


# ---------------------------------------------------------------------
# Загрузка цен из прайсов
# ---------------------------------------------------------------------

def load_prices_from_file(
        file_path: str,
        col_article: int,
        col_price: int
) -> list[dict]:
    """
    Универсальная функция загрузки прайса из Excel-файла.

    Особенности:
    - выбирает нужный лист через get_sheet_index()
    - работает с файлами без заголовков (header=None)
    - пропускает строки с некорректными данными

    :param file_path: путь к Excel-файлу
    :param col_article: индекс колонки с артикулом (0-based)
    :param col_price: индекс колонки с ценой (0-based)

    :return: список словарей:
        {
            'Артикул': str,
            'Цена': float,
            'Источник': имя файла
        }
    """

    try:
        # Определяем, с какого листа читать данные
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

            # Приводим цену к float (учёт запятых и мусорных символов)
            price_str = str(row[col_price]).replace(',', '.')
            price = float(''.join(filter(lambda c: c.isdigit() or c == '.', price_str)))

            if article and price > 0:
                result.append({
                    'Артикул': article,
                    'Цена': price,
                    'Источник': os.path.basename(file_path)
                })

        except Exception:
            # Любые ошибки парсинга строки — просто пропускаем
            continue

    print(
        f"📦 Обработан файл: {os.path.basename(file_path)}, "
        f"записей: {len(result)}"
    )

    return result


# ---------------------------------------------------------------------
# Вспомогательные утилиты
# ---------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Нормализует строку:
    - приводит к нижнему регистру
    - нормализует Unicode (важно для кириллицы)
    """
    return unicodedata.normalize("NFC", text.lower())


def get_sheet_index(file_path: str) -> int:
    """
    Возвращает индекс листа Excel, из которого нужно читать данные.

    Если файл присутствует в SHEET_INDEX_BY_FILENAME —
    используется указанный индекс листа.
    В противном случае используется первый лист (0).

    :param file_path: путь к Excel-файлу
    :return: индекс листа (0-based)
    """
    filename = normalize(os.path.basename(file_path))
    return SHEET_INDEX_BY_FILENAME.get(filename, 0)


def chunked(iterable, size: int = 60):
    """
    Делит итерируемый объект на части фиксированного размера.

    Используется, например, для пакетной обработки API-запросов.
    """
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]


# ---------------------------------------------------------------------
# Работа с файлами результатов
# ---------------------------------------------------------------------

def remove_yesterday_file() -> None:
    """
    Удаляет файл результатов за вчерашний день,
    сформированный функцией save_excel().
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


def clear_prices_folder(folder: str = 'prices') -> None:
    """
    Удаляет все Excel-файлы (.xls и .xlsx) в папке prices.
    Используется для очистки после обработки.
    """
    files = glob.glob(os.path.join(folder, '*.xls*'))

    for f in files:
        try:
            os.remove(f)
        except Exception:
            continue


def save_excel(
        data: list[dict],
        directory: str = 'results',
        file_name: str = 'result_data',
        sheet_name: str = 'Лист1'
) -> None:
    """
    Сохраняет данные в Excel-файл.

    Поведение:
    - если файл не существует — создаётся
    - если существует — данные дописываются в конец

    Имя файла формируется как:
    {file_name}_DD-MM-YYYY.xlsx

    :param data: список словарей с данными
    :param directory: папка для сохранения
    :param file_name: базовое имя файла
    :param sheet_name: имя листа Excel
    """

    cur_date = datetime.now().strftime('%d-%m-%Y')
    file_path = f'{directory}/{file_name}_{cur_date}.xlsx'

    # Создаем директорию для результатов
    os.makedirs(directory, exist_ok=True)

    # Если файл отсутствует, создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

    # Читаем существующие данные
    df_existing = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows = len(df_existing.index)

    # Добавляем новые строки
    new_df = DataFrame(data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows,
            header=(num_existing_rows == 0),
            sheet_name=sheet_name,
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')
