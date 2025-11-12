# main.py

import os
from datetime import datetime

from processor import process_all_csv


def main():
    """Основная точка входа в программу"""
    start_time = datetime.now()

    try:
        input_folder = os.path.join(os.getcwd(), 'csv_data')
        output_folder = os.path.join(os.getcwd(), 'results')

        process_all_csv(input_folder, output_folder)

    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')

    input("Нажмите Enter, чтобы закрыть программу...")


if __name__ == '__main__':
    main()
