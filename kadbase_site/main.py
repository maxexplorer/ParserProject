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
    records = []

    for land_record in root.findall('.//land_record'):
        obj = land_record.find('./object')
        if obj is None:
            continue

        # Проверка типа объекта
        type_el = obj.find('./common_data/type/value')
        if type_el is None or type_el.text != 'Земельный участок':
            continue

        # Кадастровый номер
        cad_number = (obj.findtext('./common_data/cad_number') or '').strip() or None

        # Адрес
        address = (land_record.findtext('./address_location/address/readable_address') or '').strip() or None

        # Площадь
        area_val = land_record.findtext('./params/area/value')
        area_unit = land_record.findtext('./params/area/unit')  # иногда может отсутствовать
        if not area_val:  # fallback на квартал блока
            area_val = land_record.findtext('../../area_quarter/area')
            area_unit = land_record.findtext('../../area_quarter/unit')
        if area_val:
            area = f"{area_val.strip()} {area_unit.strip()}" if area_unit else area_val.strip()
        else:
            area = None

        # Категория земель
        category = (land_record.findtext('./params/category/type/value') or '').strip() or None

        # Вид разрешенного использования
        permitted_use = (land_record.findtext(
            './params/permitted_use/permitted_use_established/by_document') or '').strip() or None

        # Кадастровая стоимость
        cad_cost = (land_record.findtext('./cost/value') or '').strip() or None

        records.append({
            'Кадастровый номер': cad_number,
            'Вид объекта недвижимости': 'Земельный участок',
            'Адрес': address,
            'Площадь или основная характеристика': area,
            'Категория земель': category,
            'Вид разрешенного использования': permitted_use,
            'Кадастровая стоимость': cad_cost,
            'Форма собственности': ''
        })

    return records


def parse_xml_file(folder: str) -> list[dict[str, str]]:
    """
    Итерируется по всем XML-файлам в папке, парсит и извлекает нужные данные по земельным участкам.
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


def save_excel(data: list[dict[str, str]], species: str) -> None:
    """
    Сохраняет собранные данные в Excel (формат .xlsx).
    """
    directory = 'results'
    os.makedirs(directory, exist_ok=True)
    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)
    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='Лист1', index=False)

    print(f'✅ Данные сохранены в файл: {file_path}')


def main():
    data_folder = 'data'  # папка с XML-файлами
    all_records = parse_xml_file(data_folder)
    save_excel(all_records, species='land_plots')


if __name__ == '__main__':
    main()
