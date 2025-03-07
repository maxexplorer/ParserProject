import os
import time
from datetime import datetime

from requests import Session
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

api_url_explain = "https://api.usersbox.ru/v1/explain"
api_url_search = "https://api.usersbox.ru/v1/search"
TOKEN = "YOUR API TOKEN"  # Замените на ваш токен

headers = {
    "Authorization": TOKEN
}


def load_inn_list():
    """Загружает список ИНН из текстового файла"""
    directory = 'data'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/data.txt'

    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def check_data(api_url_explain, inn):
    """Проверяет, есть ли утечка данных по ИНН через /explain"""

    with Session() as session:
        time.sleep(1)

        response = session.get(api_url_explain, headers=headers, params={"q": inn}, timeout=60)

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("count", 0) > 0  # True, если count > 0
    else:
        print(f"Ошибка {response.status_code} при проверке {inn}: {response.text}")
        return False


def search_data(api_url_search, inn):
    """Запрашивает данные через /search"""
    results_data = []  # Результаты для текущего ИНН

    with Session() as session:
        response = session.get(url=api_url_search, headers=headers, params={"q": inn}, timeout=60)

    if response.status_code == 200:
        data_json = response.json()
        data = data_json.get('data', {})
        items = data.get("items", [])  # Возвращает список найденных записей
    else:
        print(f"Ошибка {response.status_code} при поиске {inn}: {response.text}")
        items = []

    for item in items:
        # Получаем source на уровне записи
        source = item.get('source', {}).get('database', '')  # Извлекаем 'database' из 'source'

        hits = item.get("hits", {}).get("items", [])
        for item in hits:
            full_name = item.get('full_name')

            if not full_name:
                name = item.get('name')

                surname = item.get('surname')

                middle_name = item.get('middle_name')

                full_name = f'{surname} {name} {middle_name}'

            birth_date = item.get('birth_date')

            phone = item.get('phone')

            email = item.get('email')

            if phone or email:
                results_data.append({
                    'ИНН': inn,
                    'ФИО': full_name,
                    'Дата рождения': birth_date,
                    'Телефон': phone,
                    'Email': email,
                    'Источник': source,
                })

    return results_data


def save_excel(results_data):
    """Сохраняет результаты в Excel"""
    cur_date = datetime.now().strftime('%d-%m-%Y')

    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{cur_date}.xlsx'

    if results_data:
        dataframe = DataFrame(results_data)

        with ExcelWriter(file_path, mode='w') as writer:
            dataframe.to_excel(writer, sheet_name='data', index=False)
        print(f"Данные сохранены в {file_path}")
    else:
        print("Нет данных для сохранения.")


def main():
    inn_list = load_inn_list()
    all_results_data = []  # Переменная для всех результатов

    try:
        for inn in inn_list:
            print(f"Проверяем ИНН: {inn}")
            if check_data(api_url_explain=api_url_explain, inn=inn):
                print(f"🔍 Найдена информация по {inn}, получаем данные...")
                results_data = search_data(api_url_search=api_url_search, inn=inn)
                all_results_data.extend(results_data)  # Добавляем данные в общий список

        save_excel(results_data=all_results_data)  # Сохраняем все данные в Excel

    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
