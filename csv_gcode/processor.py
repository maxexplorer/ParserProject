# processor.py

import os
import csv
import glob
from macros import MACROS

def read_csv_files(folder: str):
    """Возвращает список всех путей к CSV файлам в папке."""
    return glob.glob(os.path.join(folder, "*.csv*"))

def process_csv_file(file_path: str, output_folder: str):
    """Обрабатывает один CSV файл по новым правилам."""
    output_lines = []
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f'{file_name}.txt')

    print(f'\n[START] Обработка файла: {file_name}.csv')

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # пропускаем заголовок

        for row_num, row in enumerate(reader, start=2):
            try:
                repeats = int(row[5])  # 6-й столбец
                length = float(row[6]) # 7-й столбец
            except (IndexError, ValueError):
                print(f'[WARN] {file_name} — строка {row_num}: некорректные 6 или 7 столбцы')
                continue

            # Собираем блок команд для этой строки
            blocks = ['0']  # начало блока
            col_idx = 12  # 13-й столбец — первая команда

            while col_idx < len(row) - 1:
                command = row[col_idx].strip()
                try:
                    y_value = float(row[col_idx + 1])
                except ValueError:
                    print(f'[WARN] {file_name} — строка {row_num}, столбец {col_idx+1}: некорректное значение Y')
                    y_value = 0.0

                if command in MACROS:
                    blocks.append(MACROS[command](0, y_value))  # x всегда 0, Y берем из CSV

                # Переходим к следующей команде (каждая команда занимает 2 столбца: команда + Y)
                col_idx += 2

            blocks.append(str(length))  # длина после всех команд
            blocks.append('')           # пустая строка как разделитель

            # Дублируем блок нужное количество раз
            for _ in range(repeats):
                output_lines.extend(blocks)

    # Запись результата
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("\n".join(output_lines))

    print(f'[DONE] Файл {file_name}.csv → {file_name}.txt')
    print(f'Всего строк: {row_num}, блоков добавлено: {len(output_lines)}')


def process_all_csv(folder: str, output_folder: str):
    """Обрабатывает все CSV в папке."""
    files = read_csv_files(folder)
    if not files:
        print('[INFO] Нет CSV файлов для обработки')
        return

    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        process_csv_file(file_path, output_folder)
