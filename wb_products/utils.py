import os
from pandas import read_excel, concat, DataFrame


import os
from pandas import read_excel, concat


def merge_excel_files(input_dir: str = 'files', output_file: str = 'result_data.xlsx') -> None:

    all_dfs = []
    all_columns = set()

    print(f'Старт объединения файлов из: {input_dir}')

    # 1. Читаем файлы
    for file in os.listdir(input_dir):
        if not file.endswith('.xlsx'):
            continue

        file_path = os.path.join(input_dir, file)

        try:
            print(f'Читаю файл: {file}')

            df = read_excel(file_path, header=1, sheet_name='Data')

            if df.empty:
                print(f'Файл {file} пустой')
                continue

            # чистим только пробелы, НО НЕ lower
            df.columns = df.columns.str.strip()

            # убираем мусорные unnamed
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

            print(f'Файл {file} загружен: {len(df)} строк, {len(df.columns)} колонок')

            all_dfs.append(df)
            all_columns.update(df.columns)

        except Exception as ex:
            print(f'Ошибка чтения {file}: {ex}')

    if not all_dfs:
        print('Нет данных для объединения')
        return

    # 2. фиксируем порядок (как есть)
    base_columns = ['Название', 'Бренд', 'Цена', 'Размер']
    other_columns = sorted(col for col in all_columns if col not in base_columns)

    final_columns = base_columns + other_columns

    print(f'Всего колонок в итоге: {len(final_columns)}')

    # 3. нормализация структуры (НЕ ИМЁН)
    normalized_dfs = []

    for df in all_dfs:
        df = df.reindex(columns=final_columns)
        normalized_dfs.append(df)

    # 4. объединение
    final_df = concat(normalized_dfs, ignore_index=True)

    # 5. чистка мусора
    final_df = final_df.loc[:, ~final_df.columns.str.contains('^Unnamed', case=False)]

    # 6. сохранение
    final_df.to_excel(output_file, index=False)

    print(f'Готово. Сохранено в {output_file}')
    print(f'Всего строк: {len(final_df)}')

def main():
    merge_excel_files(input_dir='files', output_file='result_data.xlsx')


if __name__ == '__main__':
    main()

