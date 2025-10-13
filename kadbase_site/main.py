import os
import glob
import time
import re
import xml.etree.ElementTree as ET

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pandas import DataFrame, ExcelWriter
from openpyxl import load_workbook


def init_undetected_chromedriver(headless_mode: bool = False):
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    driver.implicitly_wait(15)
    driver.maximize_window()
    return driver


def get_xml_files(folder: str) -> list[str]:
    return glob.glob(os.path.join(folder, '*.xml*'))


def extract_land_records(root: ET.Element) -> list[dict[str, str]]:
    records = []
    for land_record in root.findall('.//land_record'):
        obj = land_record.find('./object')
        if obj is None:
            continue
        type_el = obj.find('./common_data/type/value')
        if type_el is None or type_el.text != 'Земельный участок':
            continue

        cad_number = (obj.findtext('./common_data/cad_number') or '').strip() or None
        address = (land_record.findtext('./address_location/address/readable_address') or '').strip() or None
        area_val = land_record.findtext('./params/area/value')
        area_unit = land_record.findtext('./params/area/unit')
        if not area_val:
            area_val = land_record.findtext('../../area_quarter/area')
            area_unit = land_record.findtext('../../area_quarter/unit')
        area = f"{area_val.strip()} {area_unit.strip()}" if area_val and area_unit else (
            area_val.strip() if area_val else None)
        category = (land_record.findtext('./params/category/type/value') or '').strip() or None
        permitted_use = (land_record.findtext(
            './params/permitted_use/permitted_use_established/by_document') or '').strip() or None
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
    xml_files = get_xml_files(folder)
    all_records = []
    for file_path in xml_files:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            records = extract_land_records(root)
            all_records.extend(records)
        except ET.ParseError as e:
            print(f'❌ Ошибка парсинга файла {file_path}: {e}')
    return all_records


def save_excel(data: list[dict[str, str]], species: str) -> str:
    directory = 'results'
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f'result_data_{species}.xlsx')
    df = DataFrame(data)
    with ExcelWriter(file_path, mode='w') as writer:
        df.to_excel(writer, sheet_name='Лист1', index=False)
    print(f'✅ Данные сохранены в файл: {file_path}')
    return file_path


def update_ownership_excel(driver, excel_path, url):
    wb = load_workbook(excel_path)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    cad_col = headers.index('Кадастровый номер') + 1
    ownership_col = headers.index('Форма собственности') + 1

    # Считаем количество строк с кадастровыми номерами
    cad_rows = [row for row in range(2, ws.max_row + 1) if ws.cell(row=row, column=cad_col).value]
    total = len(cad_rows)
    i = 0

    for row in reversed(cad_rows):  # снизу вверх для безопасного удаления
        i += 1
        cad_number = ws.cell(row=row, column=cad_col).value
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_search"))
            )
            input_box = driver.find_element(By.CSS_SELECTOR, 'input.input_search')
            input_box.clear()
            input_box.send_keys(str(cad_number))
            input_box.send_keys(Keys.ENTER)

            ownership_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Форма собственности')]"))
            )
            ownership = ownership_div.find_element(By.XPATH, "following-sibling::div").text.strip()

            if ownership.lower() == 'частная':
                ws.delete_rows(row)
            else:
                ws.cell(row=row, column=ownership_col, value=ownership)

            print(f'Обработано номеров: {i}/{total} ({cad_number})')

        except Exception as ex:
            print(f'Ошибка обработки {cad_number}: {ex}')

    wb.save(excel_path)
    print(f'✅ Excel обновлён: {excel_path}')


def main():
    data_folder = 'data'
    url = 'https://kadbase.ru/'

    # all_records = parse_xml_file(data_folder)
    # excel_path = save_excel(all_records, species='land_plots')

    excel_path = 'results/result_data_land_plots.xlsx'

    driver = init_undetected_chromedriver(headless_mode=False)
    try:
        update_ownership_excel(driver, excel_path, url)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
