from openpyxl import load_workbook
import re

INPUT_FILE = "results/result_data.xlsx"
OUTPUT_FILE = "results/result_data_new.xlsx"

wb = load_workbook(INPUT_FILE)
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

wb.save(OUTPUT_FILE)

print(f"Готово: {OUTPUT_FILE}")