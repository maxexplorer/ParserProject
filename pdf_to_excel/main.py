import os
import shutil

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

import pdfplumber


# Функция для копирования файлов с расширением pdf из всех директорий в одну
def collect_pdfs(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.pdf'):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(destination_dir, file)
                shutil.copy(src_file, dst_file)


def extract_text_from_pdf(pdf_path):
    # Открываем PDF-файл
    with pdfplumber.open(pdf_path) as pdf:
        # Проходим по всем страницам в PDF-файле
        for page in pdf.pages:
            # Извлекаем текст со страницы
            text = page.extract_text()

            # Пример извлечения данных и добавления их в DataFrame
            # Предположим, что вы извлекаете данные из определенных строк
            data = {'Column1': 'some_data', 'Column2': 'more_data', 'Column3': 'even_more_data'}
            df = df.append(data, ignore_index=True)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/result_data.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/result_data.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='data', index=False)

    # Загружаем данные из файла
    df = read_excel('results/result_data.xlsx', sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter('results/result_data.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')

def main():
    source_directory = "C:\\Users\\mv\\Downloads\\Telegram Desktop\\PDF\\"
    destination_directory = "D:\\PycharmProjects\\ParserProject\\pdf_to_excel\\data\\"

    collect_pdfs(source_directory, destination_directory)

    # Перебор всех PDF-файлов в директории
    pdf_dir = destination_directory
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            extract_text_from_pdf(pdf_path=pdf_path)


