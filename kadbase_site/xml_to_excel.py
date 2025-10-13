import os
import glob
import xml.etree.ElementTree as ET

import pandas as pd
from pandas import DataFrame, ExcelWriter


def get_xml_files(folder: str) -> list[str]:
    """
    Возвращает список путей ко всем XML-файлам в директории.
     """
    return glob.glob(os.path.join(folder, '*.xml*'))


def extract_land_records(root: ET.Element, file_name: str) -> list[dict[str, str]]:
    """
    Извлекает кадастровые номера объектов типа 'Земельный участок'.
     """
    records: list[dict[str, str]] = []
    for obj in root.findall('.//object/common_data'):
        type_value = obj.find('./type/value')
        cad_number = obj.find('./cad_number')

        if type_value is not None and cad_number is not None:
            if type_value.text.strip() == 'Земельный участок':
                records.append({
                    'Кадастровый номер': cad_number.text.strip()
                })
    return records


def parse_xml_file(folder: str) -> list[dict[str, str]]:
    """
    Итерируется по всем XML-файлам в папке, парсит и извлекает кадастровые номера.
    """
    xml_files = get_xml_files(folder)
    all_records: list[dict[str, str]] = []

    for file_path in xml_files:
        file_name = os.path.basename(file_path)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            records = extract_land_records(root, file_name)
            all_records.extend(records)
        except ET.ParseError as e:
            print(f'❌ Ошибка парсинга файла {file_name}: {e}')

    return all_records


def save_excel(data: list, species: str) -> None:
    """
    Сохраняет собранные данные в Excel (формат .xlsx).

    :param data: Список словарей с данными товаров
    :param species: Тип данных (для названия файла)
    """
    directory = 'results'
    os.makedirs(directory, exist_ok=True)

    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)

    # Запись в Excel
    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='Лист1', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    data_folder = 'data'

    all_records = parse_xml_file(data_folder)
    save_excel(all_records, species='cadastral_number')


if __name__ == '__main__':
    main()
