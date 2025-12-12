import os
import glob
import pandas as pd

def process_excel_file(path: str) -> list:
    """
    Обрабатывает один Excel-файл и извлекает наименование, артикулы, количество и цену.

    Артикулы суммируются по количеству, а цена и наименование берутся из строки группы
    (столбец 6 = количество, столбец 7 = цена, столбец 2 = наименование). Пропускаются первые 4 строки.

    :param path: путь к Excel-файлу
    :return: список словарей с ключами 'Наименование', 'Артикул', 'Количество', 'Цена'
    """
    df: pd.DataFrame = pd.read_excel(path, header=None, skiprows=4)

    results_dict = {}
    current_price = None
    current_name = None

    for i in range(len(df)):
        row = df.iloc[i]

        # ------------------------------
        # 1) Строка группы: есть количество и цена
        # ------------------------------
        if pd.notna(row[5]) and pd.notna(row[6]):
            try:
                current_price = float(str(row[6]).replace(' ', '').replace(',', '.'))
            except Exception:
                current_price = None

            if pd.notna(row[1]):
                current_name = str(row[1]).strip()
            continue

        # ------------------------------
        # 2) Строка с артикулом
        # ------------------------------
        if isinstance(row[2], str) and row[2].startswith('BNN'):
            article: str = row[2]

            if article not in results_dict:
                results_dict[article] = {
                    'Наименование': current_name,
                    'Количество': 0,
                    'Цена': current_price
                }

            results_dict[article]['Количество'] += 1

    results = []
    for k, v in results_dict.items():
        results.append({
            'Наименование': v['Наименование'],
            'Артикул': k,
            'Количество': v['Количество'],
            'Цена': v['Цена']
        })

    return results


def save_result(results: list, source_file: str) -> None:
    """
    Сохраняет обработанные данные в новый Excel-файл.

    :param results: список словарей с данными
    :param source_file: исходный файл Excel (для формирования имени результата)
    """
    os.makedirs('results', exist_ok=True)

    base_name = os.path.basename(source_file).rsplit('.', 1)[0]
    out_path = f'results/{base_name}_result_data.xlsx'

    df: pd.DataFrame = pd.DataFrame(results)
    df.to_excel(out_path, index=False)

    print(f'✅ Результат сохранён: {out_path}')


def main(folder: str = 'data') -> None:
    """
    Основная функция, обрабатывает все Excel-файлы в указанной папке.

    :param folder: папка, в которой искать Excel-файлы
    """
    files = glob.glob(os.path.join(folder, '*.xls')) + glob.glob(os.path.join(folder, '*.xlsx'))

    if not files:
        print('❗ В папке data/ нет Excel-файлов (.xls или .xlsx)')
        return

    for file in files:
        print(f'📄 Обрабатываю: {file}')
        results: list = process_excel_file(file)
        save_result(results, file)


if __name__ == '__main__':
    main()
