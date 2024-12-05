import time

import requests

import pandas as pd
import xml.etree.ElementTree as ET


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


# Основная функция
def process_excel(input_file, output_file, interval=5):
    # Загружаем данные из входного файла
    try:
        df = pd.read_excel(input_file, sheet_name=0, skiprows=9, header=0)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return

    # Обработка каждой строки
    for index, row in df.iterrows():
        brand = row.loc['Номенклатура.Производитель']
        code = row.loc['Артикул']

        if pd.isna(brand) or pd.isna(code):
            continue

        # Выполняем запрос к API
        print(f"Отправляем запрос для артикула: {code}, бренд: {brand}")
        price_data = get_price_from_api(login='pheonix1', password='pPHOENIX11', code=code, brand=brand)

        if price_data:
            # Здесь нужно парсить ответ и извлекать нужную информацию, например цену
            # Пример парсинга: (зависит от структуры ответа)
            # price = extract_price_from_response(price_data)
            # Для примера запишем весь ответ
            price = price_data

            # Обновляем цену в DataFrame
            df.at[index, "Цена"] = price

        # Интервал между запросами
        time.sleep(interval)

    # Сохраняем результаты в новый файл
    try:
        df.to_excel(output_file, index=False)
        print(f"Результаты сохранены в {output_file}")
    except Exception as e:
        print(f"Ошибка записи файла: {e}")


# Точка входа
if __name__ == "__main__":
    # Укажите путь к файлу с артикулами и брендами
    input_file = "data/data.xlsx"  # Входной файл
    output_file = "result/result.xlsx"  # Файл с результатами
    interval = 5  # Интервал между запросами в секундах

    process_excel(input_file, output_file, interval)
