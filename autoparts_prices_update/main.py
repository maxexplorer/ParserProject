import os
from datetime import datetime
from openpyxl import load_workbook


def read_old_articles_data(old_articles_file):
    """Чтение данных из файла 'старые артикулы.xlsx'"""
    wb = load_workbook(old_articles_file)
    ws = wb.active

    articles_dict = {}

    for row in ws.iter_rows(min_row=2, max_col=2):
        name = row[0].value      # Наименование
        article = row[1].value   # Артикул

        if not name or not article:
            continue

        try:
            articles_dict[name.strip()] = str(article).strip()
        except Exception as ex:
            print(f'read_old_articles_data: {name} error: {ex}')

    return articles_dict


def update_new_articles_file(new_articles_file, articles_dict):
    """Заполнение столбца 'Старый артикул' в файле 'новые артикулы.xlsx'"""
    wb = load_workbook(new_articles_file)
    ws = wb.active

    updated_count = 0

    for row in ws.iter_rows(min_row=2, max_col=3):
        name_cell = row[0]        # Наименование
        old_article_cell = row[2] # Старый артикул

        if not name_cell.value:
            continue

        name = name_cell.value.strip()

        if name in articles_dict:
            old_article_cell.value = articles_dict[name]
            updated_count += 1

    wb.save(new_articles_file)
    print(f'Обновлено строк: {updated_count}')


def main():
    start_time = datetime.now()

    try:
        old_articles_file_path = 'data/старые артикулы.xlsx'
        new_articles_file_path = 'data/новые артикулы.xlsx'

        articles_dict = read_old_articles_data(old_articles_file_path)
        update_new_articles_file(new_articles_file_path, articles_dict)

    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Обработка завершена!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
