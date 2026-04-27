import os
from pandas import read_excel
from openpyxl import Workbook


def merge_excel_files(input_dir: str = 'results', output_file: str = 'result_data.xlsx') -> None:

    print(f'Старт объединения файлов из: {input_dir}')

    wb = Workbook(write_only=True)
    ws = wb.create_sheet()

    all_columns = set()
    header_written = False

    files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]

    # 1. сначала собираем все колонки (без загрузки всех df в память)
    for file in files:
        file_path = os.path.join(input_dir, file)

        try:
            df = read_excel(file_path, header=1, sheet_name='Data', nrows=1)

            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

            all_columns.update(df.columns)

        except Exception as ex:
            print(f'Ошибка чтения (columns) {file}: {ex}')

    base_columns = ['Название', 'Бренд', 'Цена', 'Размер']
    other_columns = sorted(col for col in all_columns if col not in base_columns)
    final_columns = base_columns + other_columns

    print(f'Всего колонок: {len(final_columns)}')

    # 2. пишем header
    ws.append(final_columns)
    header_written = True

    total_rows = 0

    # 3. читаем файлы по одному и сразу пишем
    for file in files:
        file_path = os.path.join(input_dir, file)

        try:
            print(f'Читаю файл: {file}')

            df = read_excel(file_path, header=1, sheet_name='Data')

            if df.empty:
                continue

            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

            # нормализация под общий набор колонок
            df = df.reindex(columns=final_columns)

            # запись построчно
            for row in df.itertuples(index=False, name=None):
                ws.append(row)

            total_rows += len(df)

            print(f'Добавлено строк: {len(df)}')

        except Exception as ex:
            print(f'Ошибка чтения {file}: {ex}')

    # 4. сохраняем
    wb.save(output_file)

    print(f'Готово. Сохранено в {output_file}')
    print(f'Всего строк: {total_rows}')


def main():
    merge_excel_files(input_dir='results', output_file='result_data.xlsx')


if __name__ == '__main__':
    main()