# processor.py

import os
import csv
import glob
from typing import List, Tuple

from data import gcode_header
from macros import command_map
from command_processor import CommandProcessor


def process_all_csv(folder: str, output_folder: str) -> None:
    """
    Обрабатывает все CSV-файлы в указанной папке и сохраняет результат в output_folder.

    Args:
        folder (str): Путь к папке с CSV файлами.
        output_folder (str): Путь к папке, куда сохраняются результаты.
    """
    files = glob.glob(os.path.join(folder, "*.csv*"))

    if not files:
        print('[INFO] Нет CSV файлов')
        return

    os.makedirs(output_folder, exist_ok=True)

    for file_path in files:
        process_csv_file(file_path, output_folder)


def extract_commands(row: List[str]) -> List[Tuple[str, float]]:
    """
    Извлекает команды и координаты Y из строки CSV,
    оставляя только команды, присутствующие в command_map.

    Args:
        row (List[str]): Одна строка CSV файла.

    Returns:
        List[Tuple[str, float]]: Список кортежей (command, y), фильтрованных по command_map.
    """
    commands: List[Tuple[str, float]] = []
    col_idx = 12

    while col_idx < len(row) - 1:
        command = row[col_idx].strip().upper()
        try:
            y = float(row[col_idx + 1])
        except ValueError:
            col_idx += 2
            continue

        if command in command_map:
            commands.append((command, y))

        col_idx += 2

    return commands


def calculate_deltas(commands: List[Tuple[str, float]]) -> Tuple[List[Tuple[str, float]], float]:
    """
    Преобразует абсолютные координаты Y в относительные дельты.
    Для первой команды delta = value - value (т.е. 0).

    Args:
        commands (List[Tuple[str, float]]): Список команд с абсолютными Y.

    Returns:
        Tuple[List[Tuple[str, float]], float]: Список команд с дельтами Y и последнее значение Y.
    """
    result: List[Tuple[str, float]] = []
    prev: float | None = None

    for command, y in commands:
        if prev is None:
            delta = y - y  # первая команда
        else:
            delta = y - prev

        result.append((command, round(delta, 2)))
        prev = y

    last_y: float = prev if prev is not None else 0.0
    return result, last_y


def process_csv_file(file_path: str, output_folder: str) -> None:
    """
    Обрабатывает один CSV файл:
    - Считывает повторения и длину деталей
    - Извлекает команды и дельты
    - Генерирует блоки G-кода через CommandProcessor
    - Дублирует блоки по количеству повторений
    - Сохраняет результат в output_folder

    Args:
        file_path (str): Путь к CSV файлу.
        output_folder (str): Путь к папке для сохранения TXT.
    """
    output_lines: List[str] = []

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f'{file_name}.txt')

    print(f'\n[START] {file_name}.csv')

    # добавляем G-код заголовка
    output_lines.extend(gcode_header)

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # пропускаем заголовок

        for row_num, row in enumerate(reader, start=2):
            try:
                repeats = int(row[5])  # 6-й столбец
                length = float(row[6])  # 7-й столбец
            except (IndexError, ValueError):
                print(f'[WARN] строка {row_num}')
                continue

            name = row[1] if len(row) > 1 else "unknown"

            # блок для каждой строки
            blocks: List[str] = [
                f'(name="{name}")',
                '0'
            ]

            commands = extract_commands(row)
            if not commands:
                continue

            delta_commands, last_y = calculate_deltas(commands)

            # создаем процессор для генерации G-кода
            processor = CommandProcessor()
            processor.blocks = blocks
            processor.last_y = last_y

            processor.process(delta_commands)
            processor.finalize(length)

            blocks.append(str(length))
            blocks.append('')

            # дублируем блоки по repeats
            for _ in range(repeats):
                output_lines.extend(blocks)

    # запись в файл
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(output_lines))

    print(f'[DONE] {file_name}.txt')