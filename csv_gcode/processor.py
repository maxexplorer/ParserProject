# processor.py

import os
import csv
import glob

from macros import macros, command_map
from data import gcode_header


def process_all_csv(folder: str, output_folder: str):
    """Обрабатывает все CSV в папке."""
    files = read_csv_files(folder)
    if not files:
        print('[INFO] Нет CSV файлов для обработки')
        return

    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        process_csv_file(file_path, output_folder)


def read_csv_files(folder: str):
    """Возвращает список всех путей к CSV файлам в папке."""
    return glob.glob(os.path.join(folder, "*.csv*"))


def process_csv_file(file_path: str, output_folder: str):
    """Обрабатывает один CSV файл по новым правилам с использованием command_map."""
    output_lines = []
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f'{file_name}.txt')

    print(f'\n[START] Обработка файла: {file_name}.csv')

    # 📌 Добавляем G-коды инициализации в начало
    output_lines.extend(gcode_header)

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # пропускаем заголовок

        for row_num, row in enumerate(reader, start=2):
            try:
                repeats = int(row[5])  # 6-й столбец
                length = float(row[6])  # 7-й столбец
            except (IndexError, ValueError):
                print(f'[WARN] {file_name} — строка {row_num}: некорректные 6 или 7 столбцы')
                continue

            name_idx = 1
            col_idx = 12  # 13-й столбец — первая команда

            # Получаем имя (например, из второго столбца)
            try:
                name = row[name_idx].strip()
            except IndexError:
                name = "unknown"

            # 📌 Создаём блок уже с именем
            blocks = [f'(name="{name}")', '0']

            commands_in_row = []

            # Считываем все команды в строке
            while col_idx < len(row) - 1:
                csv_command = row[col_idx].strip()
                try:
                    y_value = float(row[col_idx + 1])
                    #TODO y_value - prev_value
                except ValueError:
                    print(f'[WARN] {file_name} — строка {row_num}, столбец {col_idx + 1}: некорректное значение Y')
                    y_value = 0.0

                if csv_command in command_map:
                    macro_key = command_map[csv_command]

                    if isinstance(macro_key, tuple):
                        start_macro, finish_macro = macro_key
                        if col_idx == 12:
                            blocks.extend(macros[start_macro](y_value).splitlines())
                    else:
                        blocks.extend(macros[macro_key](y_value).splitlines())

                    commands_in_row.append(csv_command)

                col_idx += 2

            # Вставка команд в конце строки
            last_command = commands_in_row[-1] if commands_in_row else None

            if last_command and last_command.startswith('END_TRUSS'):
                blocks.extend(macros[finish_macro](length).splitlines())
                blocks.extend(macros['CUT_LENGTH'](length).splitlines())
            else:
                blocks.extend(macros['CUT'](length).splitlines())

            # Добавляем длину и пустую строку
            blocks.append(str(length))
            blocks.append('')

            # Дублируем блок нужное количество раз
            for _ in range(repeats):
                output_lines.extend(blocks)

    # Запись результата
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(output_lines))

    print(f'[DONE] Файл {file_name}.csv → {file_name}.txt')
    print(f'Всего строк: {row_num}, блоков добавлено: {len(output_lines)}')
