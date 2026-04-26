import os
from pandas import read_excel, concat, DataFrame


def merge_excel_files(input_dir: str = 'files', output_file: str = 'result_data.xlsx') -> None:
    """
    Объединяет все Excel-файлы из папки в один файл.

    Условия:
    - первые 4 колонки одинаковые
    - остальные могут отличаться
    - одинаковые названия колонок не дублируются
    - отсутствующие значения заполняются NaN
    - удаляются дубликаты

    :param input_dir: папка с Excel файлами
    :param output_file: итоговый файл
    """

    all_dfs = []
    all_columns = set()

    # 1. Читаем все файлы
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx'):
            file_path = os.path.join(input_dir, file)

            try:
                df = read_excel(file_path, sheet_name='Data')
                if df.empty:
                    continue

                # Убираем возможные пробелы в названиях колонок
                df.columns = [col.strip() for col in df.columns]

                all_dfs.append(df)
                all_columns.update(df.columns)

            except Exception as ex:
                print(f'Ошибка чтения {file}: {ex}')

    if not all_dfs:
        print('Нет данных для объединения')
        return

    # 2. Общий список колонок (фиксируем порядок)
    base_columns = ['Название', 'Бренд', 'Цена', 'Размер']
    other_columns = sorted(col for col in all_columns if col not in base_columns)

    final_columns = base_columns + other_columns

    normalized_dfs = []

    # 3. Приводим каждый DataFrame к общему виду
    for df in all_dfs:
        for col in final_columns:
            if col not in df.columns:
                df[col] = None

        df = df[final_columns]
        normalized_dfs.append(df)

    # 4. Объединяем
    final_df = concat(normalized_dfs, ignore_index=True)

    # 6. Сохраняем
    final_df.to_excel(output_file, index=False)

    print(f'Готово. Сохранено в {output_file}')
    print(f'Всего строк: {len(final_df)}')

def main():
    merge_excel_files(input_dir='data', output_file='result_data.xlsx')


if __name__ == '__main__':
    main()

