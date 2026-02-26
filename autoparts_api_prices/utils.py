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

from pandas import DataFrame, ExcelWriter, read_excel, read_csv
import unicodedata


# ---------------------------------------------------------------------
# Конфигурация листов Excel
# ---------------------------------------------------------------------

# Маппинг: имя файла → индекс листа с данными
# Используется, если в файле есть служебный (скрытый) лист,
# который необходимо пропустить.
SHEET_INDEX_BY_FILENAME = {
    'авто-парти.xls': 1,  # Прайс.xls → данные находятся на 2-м листе
}


# ---------------------------------------------------------------------
# Загрузка артикулов из data/
# ---------------------------------------------------------------------

def load_articles_from_data(folder: str = 'data') -> tuple[dict, DataFrame, str] | tuple[dict, None, None]:
    """
    Загружает артикулы из исходного Excel-файла в папке data/,
    группируя их по производителю (импортеру алкогольной продукции).

    :param folder: папка с Excel-файлами
    :return: Словарь:
        {
            "ООО \"А-2\" - 0": ["FFG22779", "NG20263", ...],
            ...
        }, df исходного файла, путь к файлу
    """

    files = glob.glob(os.path.join(folder, '*.xls*'))
    if not files:
        print('❗ В папке data/ нет Excel-файлов (.xls или .xlsx)')
        return {}, None, None

    # Используем первый найденный файл
    file_path = files[0]
    df = read_excel(file_path)
    df.columns = df.columns.str.strip()

    # Убираем строки без артикула или производителя
    df = df.dropna(subset=[df.columns[2], df.columns[5]])

    articles_by_manufacturer = {}

    for row in df.itertuples(index=False):
        manufacturer = str(row[2]).strip()  # 3-я колонка: Производитель (импортер)
        brand = str(row[3]).strip()  # 4-я колонка: Производитель (бренд)
        article = str(row[5]).strip()       # 6-я колонка: Артикул

        if manufacturer not in articles_by_manufacturer:
            articles_by_manufacturer[manufacturer] = []

        articles_by_manufacturer[manufacturer].append((article, brand))

    print(f"Загружено производителей: {len(articles_by_manufacturer)}")

    return articles_by_manufacturer, df, file_path


# ---------------------------------------------------------------------
# Загрузка цен из прайсов
# ---------------------------------------------------------------------

def load_prices_from_file(
        file_path: str,
        article_col: int,
        price_col: int,
        quantity_col,
        name_col
) -> list[dict]:
    """
    Универсальная функция загрузки прайса из Excel-файла.

    Особенности:
    - выбирает нужный лист через get_sheet_index()
    - работает с файлами без заголовков (header=None)
    - пропускает строки с некорректными данными

    :param file_path: путь к Excel-файлу
    :param article_col: индекс колонки с артикулом (0-based)
    :param price_col: индекс колонки с ценой (0-based)
    :param quantity_col: индекс колонки с количеством
    :param name_col: индекс колонки с наименованием производителя

    :return: список словарей:
        {
            'Артикул': str,
            'Цена': float,
            'Количество': int,
            'Наименование произваодителя': str
        }
    """

    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.csv':
            df = read_csv(
                file_path,
                header=None,
                sep=';',
                encoding='cp1251',
                on_bad_lines='skip'
            )
        else:
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
            article = str(row[article_col]).strip()

            # Приводим цену к float (учёт запятых и мусорных символов)
            price_str = str(row[price_col]).replace(',', '.')
            price = float(''.join(filter(lambda c: c.isdigit() or c == '.', price_str)))

            quantity = str(row[quantity_col]).strip()

            manufacturer_name = str(row[name_col]).strip()

            if article and price > 0:
                result.append({
                    'Артикул': article,
                    'Цена': price,
                    'Количество': quantity,
                    'Наименование производителя': manufacturer_name,
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

    if not files:
        print(f"[INFO] В папке '{folder}' нет файлов для удаления")
        return

    removed_count = 0

    for f in files:
        try:
            os.remove(f)
            removed_count += 1
        except Exception:
            continue

    print(f"[OK] В папке '{folder}' удалено файлов: {removed_count}")



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
