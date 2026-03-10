# processor.py

import os
import csv
import glob

from data import gcode_header
from command_processor import CommandProcessor


def process_all_csv(folder: str, output_folder: str):
    files = glob.glob(os.path.join(folder, "*.csv*"))

    if not files:
        print('[INFO] Нет CSV файлов')
        return
    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        process_csv_file(file_path, output_folder)


def extract_commands(row):
    commands = []
    col_idx = 12

    while col_idx < len(row) - 1:
        command = row[col_idx].strip()
        try:
            y = float(row[col_idx + 1])
        except ValueError:
            col_idx += 2
            continue

        commands.append((command, y))

        col_idx += 2

    return commands


def calculate_deltas(commands):
    result = []
    prev = None

    for command, y in commands:
        if prev is None:
            delta = y - y
        else:
            delta = y - prev

        result.append((command, delta))

        prev = y

    return result, prev


def process_csv_file(file_path: str, output_folder: str):
    output_lines = []

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f'{file_name}.txt')

    print(f'\n[START] {file_name}.csv')

    output_lines.extend(gcode_header)

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)

        for row_num, row in enumerate(reader, start=2):
            try:
                repeats = int(row[5])
                length = float(row[6])
            except (IndexError, ValueError):
                print(f'[WARN] строка {row_num}')
                continue

            name = row[1] if len(row) > 1 else "unknown"

            blocks = [
                f'(name="{name}")',
                '0'
            ]

            commands = extract_commands(row)

            if not commands:
                continue

            delta_commands, last_y = calculate_deltas(commands)

            processor = CommandProcessor()

            processor.blocks = blocks
            processor.last_y = last_y

            processor.process(delta_commands)

            processor.finalize(length)

            blocks.append(str(length))
            blocks.append('')

            # Дублируем блок нужное количество раз
            for _ in range(repeats):
                output_lines.extend(blocks)

    # Запись результата
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(output_lines))

    print(f'[DONE] {file_name}.txt')
