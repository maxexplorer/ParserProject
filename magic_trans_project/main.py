import os

import requests

import pandas as pd
from pandas import DataFrame
from pandas import ExcelWriter
import openpyxl


def get_excel_file():
    # URL-адрес Excel файла для скачивания
    excel_url = "https://pecom.ru/upload/tarifi/v_g_moskva.xls"

    name_file_excel = excel_url.split('/')[-1].split('.')[0]

    # Отправляем GET-запрос для скачивания файла
    response = requests.get(excel_url)

    # Проверяем успешность запроса
    if response.status_code == 200:

        # Если папка data не создана, то создаём
        if not os.path.exists('data'):
            os.makedirs('data')

        # Открываем файл для записи в бинарном режиме
        with open(f"data/{name_file_excel}.xls", "wb") as file:
            # Записываем содержимое ответа в файл
            file.write(response.content)
        print("Файл успешно скачан")
    else:
        print("Ошибка при скачивании файла:", response.status_code)


def get_excel_file_pandas():

    # Ссылка на файл XLS
    xls_url = "https://pecom.ru/upload/tarifi/v_g_moskva.xls"

    # Создаём имя файла из ссылки
    name_file_excel = xls_url.split('/')[-1].split('.')[0]

    # Чтение файла XLS по ссылке
    dataframe = pd.read_excel(xls_url)

    # Сохранение данных в файл XLSX
    # dataframe.to_excel(f"data/{name_file_excel}.xlsx", index=False)
    # is equivalent to
    with ExcelWriter(f"data/{name_file_excel}.xlsx", mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='ПЭК', index=False)


def load_excel_file():
    # # Открываем файл Excel
    # workbook = openpyxl.load_workbook("data/v_g_moskva.xls")

    # Чтение данных из файла Excel, пропуск первых 3 строк и выбор конкретного листа
    df = pd.read_excel("data/v_g_moskva.xlsx")
 

    for i, row in df.iterrows():
        print(i, row[1])


def main():
    # get_excel_file()
    load_excel_file()
    # get_excel_file_pandas()


if __name__ == '__main__':
    main()
