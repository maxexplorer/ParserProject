import os
import glob

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill


ADDED_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")   # зелёный
REMOVED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # красный
CHANGED_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # жёлтый


def load_excel(path):
    df = pd.read_excel(path, dtype=str)
    df.columns = df.columns.str.strip()
    df = df.fillna('')
    return df


def compare_data(old_df, new_df, key_column='Артикул'):
    old_df = old_df.set_index(key_column)
    new_df = new_df.set_index(key_column)

    added_keys = new_df.index.difference(old_df.index)
    removed_keys = old_df.index.difference(new_df.index)
    common_keys = new_df.index.intersection(old_df.index)

    changes = {}

    for key in common_keys:
        row_changes = {}
        for col in new_df.columns:
            old_val = old_df.at[key, col] if col in old_df.columns else ''
            new_val = new_df.at[key, col] if col in new_df.columns else ''
            if str(old_val).strip() != str(new_val).strip():
                row_changes[col] = True
        if row_changes:
            changes[key] = row_changes

    return added_keys, removed_keys, changes


def apply_formatting(result_path, added, removed, changed, key_column='Артикул'):
    wb = load_workbook(result_path)
    ws = wb.active

    header = {cell.value: idx for idx, cell in enumerate(ws[1])}
    key_idx = header.get(key_column)

    for row in ws.iter_rows(min_row=2):
        key = str(row[key_idx].value).strip()

        if key in added:
            for cell in row:
                cell.fill = ADDED_FILL

        elif key in changed:
            for col, is_changed in changed[key].items():
                if is_changed:
                    col_idx = header.get(col)
                    if col_idx is not None:
                        row[col_idx].fill = CHANGED_FILL

    # Добавим удалённые товары в конец
    last_row = ws.max_row + 1
    for key in removed:
        ws.cell(row=last_row, column=key_idx + 1, value=key).fill = REMOVED_FILL
        for col, idx in header.items():
            if col == key_column:
                continue
            ws.cell(row=last_row, column=idx + 1, value='(Удалён)').fill = REMOVED_FILL
        last_row += 1

    wb.save(result_path)


def save_result(new_df, output_path='result.xlsx'):
    folder = os.path.dirname(output_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    new_df.to_excel(output_path, index=False)
    return output_path


def main():
    folder = 'data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    old_path = excel_files[0]
    new_path = excel_files[1]
    result_path = 'results/compared.xlsx'

    print('📁 Загружаю таблицы...')
    old_df = load_excel(old_path)
    new_df = load_excel(new_path)

    print('🔍 Сравнение данных...')
    added, removed, changed = compare_data(old_df, new_df)

    print('💾 Сохраняю результат...')
    result_file = save_result(new_df, result_path)

    print('🎨 Применяю форматирование...')
    apply_formatting(result_file, added, removed, changed)

    print(f'✅ Готово! Результат: {result_file}')


if __name__ == '__main__':
    main()
