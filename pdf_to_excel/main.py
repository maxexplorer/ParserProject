import os
import shutil
from datetime import datetime

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

import pdfplumber

start_time = datetime.now()


# Функция для копирования файлов с расширением pdf из всех директорий в одну
def collect_pdfs(source_dir):
    count = 1

    if not os.path.exists('data2'):
        os.makedirs('data2')

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.pdf'):
                src_file = os.path.join(root, file)
                dst_file = os.path.join('data2', file)
                shutil.copy(src_file, dst_file)
        print(f'Обработано: {count}')

        count += 1


def extract_text_from_pdf(pdf_path: str) -> list:
    result_data = []
    information_about_copyright_holder_lst = []
    document_basis_lst = []

    cadastral_number = None
    assignment = None
    address = None
    cadastral_price = None
    registration_number = None
    information_about_copyright_holder1 = None
    information_about_copyright_holder2 = None
    type_registered_restriction_right = None
    document_basis1 = None
    document_basis2 = None

    # Открываем PDF-файл
    with pdfplumber.open(pdf_path) as pdf:
        # Проходим по всем страницам в PDF-файле
        for page in pdf.pages:
            # Получаем все таблицы на странице
            for table in page.extract_tables():
                # Проходим по строкам в таблице
                for row in table:
                    while "" in row:
                        row.remove("")
                    while None in row:
                        row.remove(None)

                    if 'Кадастровый номер' in row:
                        cadastral_number = row[-1]
                    elif 'По документу' in row:
                        assignment = row[-1]
                    elif 'Адрес в соответствии с ФИАС (Текст)' in row:
                        address = row[-1]
                    elif 'Кадастровая стоимость' in row:
                        cadastral_price = row[-1]
                    elif 'Номер регистрации вещного права' in row:
                        registration_number = row[-1]
                    elif 'Сведения о правообладателе' in row:
                        information_about_copyright_holder_lst.append(row[-1])
                    elif 'Вид зарегистрированного ограничения права или обременения объекта недвижимости' in row:
                        type_registered_restriction_right = row[-1]
                    elif 'Сведения о правообладателе' in row:
                        information_about_copyright_holder_lst.append(row[-1])
                    elif 'Документ-основание' in row:
                        document_basis_lst.append(row[-1])

        if information_about_copyright_holder_lst:
            information_about_copyright_holder1 = information_about_copyright_holder_lst[0]
        if len(information_about_copyright_holder_lst) > 1:
            information_about_copyright_holder2 = information_about_copyright_holder_lst[1]

        if document_basis_lst:
            document_basis1 = document_basis_lst[0]
        if len(document_basis_lst) > 1:
            document_basis2 = document_basis_lst[1]

        result_data.append(
            {
                'Кадастровый номер': cadastral_number,
                'По документу': assignment,
                'Адрес в соответствии с ФИАС': address,
                'Кадастровая стоимость': cadastral_price,
                'Номер регистрации вещного права': registration_number,
                'Сведения о правообладателе 1': information_about_copyright_holder1,
                'Вид зарегистрированного ограничения права или обременения объекта недвижимости 1': type_registered_restriction_right,
                'Сведения о правообладателе 2': information_about_copyright_holder2,
                'Документ-основание 1': document_basis1,
                'Документ-основание 2': document_basis2

            }
        )

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/result_data2.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/result_data2.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='data', index=False)

    # Загружаем данные из файла
    df = read_excel('results/result_data2.xlsx', sheet_name='data')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter('results/result_data2.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='data',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    # source_directory = "C:\\Users\\mv\\Downloads\\Telegram Desktop\\PDF1\\"
    #
    # collect_pdfs(source_directory)

    # Перебор всех PDF-файлов в директории
    pdf_dir = 'data2'
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            result_data = extract_text_from_pdf(pdf_path=pdf_path)
            save_excel(data=result_data)
            print(f'Обработано: {filename}')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
