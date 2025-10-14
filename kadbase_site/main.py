# ===============================
# 📄 Импорты
# ===============================
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


# ===============================
# 🧭 Инициализация браузера
# ===============================
def init_undetected_chromedriver(headless_mode: bool = False):
    """
    Инициализирует браузер Chrome с использованием undetected_chromedriver.

    :param headless_mode: если True — браузер запустится без интерфейса.
    :return: объект WebDriver.
    """
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver = uc.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver


# ===============================
# 📂 Работа с файлами XML
# ===============================
def get_xml_files(folder: str) -> list[str]:
    """
    Возвращает список всех XML-файлов в указанной папке.
    """
    return glob.glob(os.path.join(folder, '*.xml*'))


def extract_land_records(root: ET.Element) -> list[dict[str, str]]:
    """
    Извлекает данные о земельных участках из XML-дерева.
    """
    records: list[dict[str, str]] = []

    for land_record in root.findall('.//land_record'):
        obj = land_record.find('./object')
        if obj is None:
            continue

        # Проверяем, что объект — земельный участок
        type_el = obj.find('./common_data/type/value')
        if type_el is None or type_el.text != 'Земельный участок':
            continue

        # Извлекаем необходимые поля
        cad_number = (obj.findtext('./common_data/cad_number') or '').strip() or None
        address = (land_record.findtext('./address_location/address/readable_address') or '').strip() or None
        area_val = land_record.findtext('./params/area/value')
        area_unit = land_record.findtext('./params/area/unit')

        # Если основной площади нет — пробуем получить из другого блока
        if not area_val:
            area_val = land_record.findtext('../../area_quarter/area')
            area_unit = land_record.findtext('../../area_quarter/unit')

        area = f"{area_val.strip()} {area_unit.strip()}" if area_val and area_unit else (
            area_val.strip() if area_val else None
        )

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
    """
    Обрабатывает все XML-файлы в указанной папке.
    """
    xml_files: list[str] = get_xml_files(folder)
    all_records: list[dict[str, str]] = []

    for file_path in xml_files:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            records = extract_land_records(root)
            all_records.extend(records)
        except ET.ParseError as e:
            print(f'❌ Ошибка парсинга файла {file_path}: {e}')

    return all_records


# ===============================
# 📊 Сохранение в Excel
# ===============================
def save_excel(data: list[dict[str, str]], species: str) -> str:
    """
    Сохраняет данные в Excel-файл в папке 'results'.
    """
    directory = 'results'
    os.makedirs(directory, exist_ok=True)
    file_path: str = os.path.join(directory, f'result_data_{species}.xlsx')

    df = DataFrame(data)
    with ExcelWriter(file_path, mode='w') as writer:
        df.to_excel(writer, sheet_name='Лист1', index=False)

    print(f'✅ Данные сохранены в файл: {file_path}')
    return file_path


# ===============================
# 🏢 Обновление столбца "Форма собственности"
# ===============================
def update_ownership_excel(driver, excel_path: str, url: str, sheet: str = 'Лист2', batch_size: int = 10) -> None:
    """
    Обновляет данные в Excel: проверяет форму собственности по кадастровому номеру
    через сайт и удаляет строки с частной формой собственности или при отсутствии данных.
    """
    wb = load_workbook(excel_path)
    ws = wb[sheet]

    headers: list[str] = [cell.value for cell in ws[1]]
    cad_col: int = headers.index('Кадастровый номер') + 1
    ownership_col: int = headers.index('Форма собственности') + 1

    cad_rows: list[int] = [row for row in range(2, ws.max_row + 1) if ws.cell(row=row, column=cad_col).value]
    total: int = len(cad_rows)
    i: int = 0

    # Обходим строки снизу вверх, чтобы безопасно удалять
    for row in reversed(cad_rows):
        i += 1
        cad_number: str = str(ws.cell(row=row, column=cad_col).value)

        try:
            driver.get(url)

            # Ожидаем поле ввода
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_search"))
            )

            # Вводим кадастровый номер
            input_box = driver.find_element(By.CSS_SELECTOR, 'input.input_search')
            input_box.clear()
            input_box.send_keys(cad_number)
            input_box.send_keys(Keys.ENTER)

            # Проверяем наличие блока с формой собственности
            ownership_divs = driver.find_elements(By.XPATH, "//div[contains(text(),'Форма собственности')]")
            if ownership_divs:
                ownership_div = ownership_divs[0]
                ownership: str = ownership_div.find_element(By.XPATH, "following-sibling::div").text.strip()

                # Удаляем строку, если собственность частная
                if ownership.lower() == 'частная':
                    ws.delete_rows(row)
                else:
                    ws.cell(row=row, column=ownership_col, value=ownership)
            else:
                # Если блока нет — тоже удаляем строку
                ws.delete_rows(row)

            print(f'Обработано номеров: {i}/{total} ({cad_number})')

        except Exception as ex:
            print(f'Ошибка обработки {cad_number}: {ex}')

        # Промежуточное сохранение каждые batch_size записей
        if i % batch_size == 0:
            wb.save(excel_path)
            print(f'💾 Промежуточное сохранение: обработано {i}/{total}')

    # Финальное сохранение
    wb.save(excel_path)
    print(f'✅ Excel обновлён: {excel_path}')


# ===============================
# 🚀 Точка входа
# ===============================
def main() -> None:
    """
    Основная точка входа в программу:
    - загружает XML-данные (если нужно),
    - открывает браузер,
    - авторизуется на сайте,
    - обновляет Excel-файл по форме собственности.
    """
    data_folder: str = 'data'
    url: str = 'https://kadbase.ru/'

    # Если нужно — распарсить XML и создать Excel
    # all_records = parse_xml_file(data_folder)
    # excel_path = save_excel(all_records, species='land_plots')

    excel_path: str = 'results/result_data_land_plots.xlsx'

    driver = init_undetected_chromedriver(headless_mode=False)
    try:
        # Авторизация вручную
        driver.get("https://kadbase.ru/lk/")
        time.sleep(60)
        print("⏳ У вас есть 60 секунд, чтобы авторизоваться вручную...")

        update_ownership_excel(driver, excel_path, url)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
