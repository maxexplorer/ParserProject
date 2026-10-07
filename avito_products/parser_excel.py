from openpyxl import load_workbook
import re

INPUT_FILE = "results/result_data_new.xlsx"
OUTPUT_FILE = "results/result_data_new.xlsx"


def add_memory_columns(input_file, output_file):
    wb = load_workbook(input_file)
    ws = wb["data"]

    title_col = None
    price_col = None

    # Ищем номера нужных столбцов
    for cell in ws[1]:
        if cell.value == "Заголовок":
            title_col = cell.column

        elif cell.value == "Цена":
            price_col = cell.column

    if title_col is None:
        raise ValueError('Не найден столбец "Заголовок"')

    if price_col is None:
        raise ValueError('Не найден столбец "Цена"')

    # Добавляем 2 столбца после цены
    ws.insert_cols(price_col + 1, amount=2)

    ram_col = price_col + 1
    storage_col = price_col + 2

    ws.cell(row=1, column=ram_col, value="ОЗУ")
    ws.cell(row=1, column=storage_col, value="Память")

    memory_pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s*/\s*(\d{2,4})(?!\d)"
    )

    for row in range(2, ws.max_row + 1):
        title = ws.cell(row=row, column=title_col).value

        if title is None:
            continue

        match = memory_pattern.search(str(title))

        if match:
            ram = int(match.group(1))
            storage = int(match.group(2))

            ws.cell(row=row, column=ram_col, value=ram)
            ws.cell(row=row, column=storage_col, value=storage)

    wb.save(output_file)

    print(f"ОЗУ и память добавлены: {output_file}")


def move_last_photo_to_first(input_file, output_file):
    wb = load_workbook(input_file)
    ws = wb["data"]

    photo_col = None

    # Ищем столбец "Фото"
    for cell in ws[1]:
        if cell.value == "Фото":
            photo_col = cell.column
            break

    if photo_col is None:
        raise ValueError('Не найден столбец "Фото"')

    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=photo_col)

        if cell.value is None:
            continue

        # Ссылки разделены символом |
        photos = [
            photo.strip()
            for photo in str(cell.value).split("|")
            if photo.strip()
        ]

        # Если меньше двух ссылок — переставлять нечего
        if len(photos) < 2:
            continue

        # Последнюю переносим на первое место
        photos = photos[:-1]

        # Собираем обратно через |
        cell.value = " | ".join(photos)

    wb.save(output_file)

    print(f"Порядок фото изменён: {output_file}")


# ========================================
# ЗАПУСК
# ========================================

# Если нужно добавить ОЗУ и Память:
# add_memory_columns(INPUT_FILE, OUTPUT_FILE)


# Если нужно только поменять порядок фото:
move_last_photo_to_first(INPUT_FILE, OUTPUT_FILE)