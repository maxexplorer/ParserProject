import os
import glob
import pandas as pd


def process_excel_file(path: str) -> dict:
    """
    Обрабатывает Excel-файл и возвращает два блока:
    1) summary: суммарные данные по артикулу (количество, цена, наименование)
    2) serials: отдельные строки с Артикул + Серия
    """
    df: pd.DataFrame = pd.read_excel(path, header=None, skiprows=4)

    # ----------- Суммарные данные -----------
    results_dict = {}
    current_price = None
    current_name = None

    for i in range(len(df)):
        row = df.iloc[i]

        # Строка группы
        if pd.notna(row[5]) and pd.notna(row[6]):
            try:
                current_price = float(str(row[6]).replace(' ', '').replace(',', '.'))
            except Exception:
                current_price = None

            if pd.notna(row[1]):
                current_name = str(row[1]).strip()
            continue

        # Строка с артикулом
        if isinstance(row[2], str) and row[2].startswith('BNN'):
            article = row[2]
            if article not in results_dict:
                results_dict[article] = {
                    'Наименование': current_name,
                    'Количество': 0,
                    'Цена': current_price
                }
            results_dict[article]['Количество'] += 1

    summary = []
    for k, v in results_dict.items():
        summary.append({
            'Наименование': v['Наименование'],
            'Артикул': k,
            'Количество': v['Количество'],
            'Цена': v['Цена']
        })

    # ----------- Артикул + серия -----------
    serial_rows = []

    for i in range(len(df)):
        row = df.iloc[i]

        # Строка группы
        if pd.notna(row[5]) and pd.notna(row[6]):
            continue

        if isinstance(row[2], str) and row[2].startswith('BNN'):
            article = row[2]
            series = str(row[7]).strip() if pd.notna(row[7]) else None
            serial_rows.append({
                'Артикул': article,
                'Серия': series
            })

    return {'summary': summary, 'serials': serial_rows}


def save_result(processed: dict, source_file: str) -> None:
    """
    Записывает данные в ОДИН лист:
    - summary: колонки A-D
    - serials: колонки G-H (7 и 8 столбцы)
    """
    os.makedirs('results', exist_ok=True)
    base_name = os.path.basename(source_file).rsplit('.', 1)[0]
    out_path = f'results/{base_name}_result_data.xlsx'

    df_summary = pd.DataFrame(processed['summary'])
    df_serials = pd.DataFrame(processed['serials'])

    with pd.ExcelWriter(out_path) as writer:
        # Старая реализация (A-D)
        df_summary.to_excel(
            writer,
            index=False,
            sheet_name='Лист1',
            startrow=0,
            startcol=0
        )

        # Новая реализация (G-H → 7 и 8 столбцы)
        df_serials.to_excel(
            writer,
            index=False,
            sheet_name='Лист1',
            startrow=0,
            startcol=6
        )

    print(f'✅ Результат сохранён: {out_path}')


def main(folder: str = 'data') -> None:
    """
    Основная функция: обрабатывает все Excel-файлы в папке.
    """
    files = glob.glob(os.path.join(folder, '*.xls')) + glob.glob(os.path.join(folder, '*.xlsx'))

    if not files:
        print('❗ В папке data/ нет Excel-файлов (.xls или .xlsx)')
        return

    for file in files:
        print(f'📄 Обрабатываю: {file}')
        processed = process_excel_file(file)
        save_result(processed, file)


if __name__ == '__main__':
    main()
