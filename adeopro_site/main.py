import time
import requests
import xml.etree.ElementTree as ET
from openpyxl import load_workbook


# Функция для отправки одного запроса
def get_price_from_api(login: str, password: str, code: int, brand: str, force_online: int = 0,
                       crosses: str = "disallow", force_diler_replace: int = 0):
    # Формируем XML-запрос
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <message>
      <param>
        <action>price</action>
        <login>{login}</login>
        <password>{password}</password>
        <code>{code}</code>
        <brand>{brand}</brand>
        <crosses>{crosses}</crosses>
        <force_online>{force_online}</force_online>
        <force_dilerReplace>{force_diler_replace}</force_dilerReplace>
      </param>
    </message>'''

    url = "https://xml.adeo.pro/pricedetals2.php"

    try:
        # Отправляем запрос к API
        response = requests.post(url, data={'xml': xml}, timeout=60)

        # Проверяем успешность запроса
        if response.status_code == 200:
            return response.text  # Возвращаем текст ответа
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")
        return None


# Функция для извлечения минимальной цены из XML ответа
def extract_min_price_from_response(xml_data):
    # Парсим XML-ответ
    try:
        root = ET.fromstring(xml_data)
        prices = [float(detail.find('price').text) for detail in root.findall('detail')]
        min_price = min(prices) if prices else None
        return min_price
    except Exception as e:
        print(f"Ошибка при парсинге XML: {e}")
        return None


# Основная функция
def process_excel(input_file, interval=5):
    # Загружаем рабочую книгу и активный лист
    try:
        workbook = load_workbook(input_file)
        work_sheet = workbook.active  # Доступ к активному листу
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return

    # Получаем заголовки из 10-й строки
    headers = [cell.value for cell in work_sheet[10]]  # Заголовки столбцов находятся в 10-й строке

    # Индексы столбцов для "Номенклатура.Производитель" и "Артикул" по названиям
    try:
        # brand_column = headers.index('Номенклатура.Производитель') + 1  # Индексы в openpyxl начинаются с 1
        # code_column = headers.index('Артикул') + 1
        # old_price_column = headers.index('Цена') + 1
        brand_column = 1
        code_column = 4
        old_price_column = 10
        price_column = 11
    except ValueError as e:
        print(f"Ошибка: не найдены необходимые столбцы. {e}")
        return

    # Обрабатываем строки (начиная с 11-й строки, т.к. 10-я - это заголовки)
    for row_idx in range(12, work_sheet.max_row + 1):
        brand = work_sheet.cell(row=row_idx, column=brand_column).value
        code = work_sheet.cell(row=row_idx, column=code_column).value
        old_price = work_sheet.cell(row=row_idx, column=old_price_column).value

        if brand is None or code is None:
            continue

        # Выполняем запрос к API
        print(f"Отправляем запрос для артикула: {code}, бренд: {brand}")
        price_data = get_price_from_api(login='pheonix1', password='pPHOENIX11', code=code, brand=brand)

        if price_data:
            # Извлекаем минимальную цену из ответа
            min_price = extract_min_price_from_response(price_data)

            # Если минимальная цена найдена, записываем её в Excel
            if min_price is not None:
                min_price = min_price * 0.8
                work_sheet.cell(row=row_idx, column=price_column).value = min_price
            else:
                work_sheet.cell(row=row_idx,
                                column=price_column).value = old_price  # Если цена не найдена записываем старую цену
        else:
            work_sheet.cell(row=row_idx,
                            column=price_column).value = old_price  # Если данных нет, записываем старую цену

        # Интервал между запросами
        time.sleep(interval)

    # Сохраняем изменения в тот же файл
    try:
        workbook.save(input_file)  # Сохраняем в исходный файл
        print(f"Результаты сохранены в {input_file}")
    except Exception as e:
        print(f"Ошибка записи файла: {e}")


# Точка входа
if __name__ == "__main__":
    # Укажите путь к файлу с артикулами и брендами
    input_file = "data/data.xlsx"  # Входной файл
    interval = 2  # Интервал между запросами в секундах

    process_excel(input_file, interval)
