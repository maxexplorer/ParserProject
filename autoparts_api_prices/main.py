# main.py

"""
Точка входа приложения.

Скрипт:
- Загружает артикулы из Excel
- Получает цены из Autotrade и ABCP
- Сохраняет результаты в Excel
"""

import os
import hashlib
from datetime import datetime, timedelta

from autotrade import get_prices_autotrade
from abcp import get_prices_abcp

from config import login_autotrade, password_autotrade, login_abcp, password_abcp
from utils import load_article_info_from_excel, save_excel

# Фиксируем время начала выполнения
start_time: datetime = datetime.now()

# Salt для формирования auth_key Autotrade
salt: str = '1>6)/MI~{J'

# URL API
url_autotrade: str = "https://api2.autotrade.su/?json"
url_abcp: str = "https://id34451.public.api.abcp.ru/"

# -------------------
# Формируем auth_key для autotrade
# -------------------
password_md5_autotrade: str = hashlib.md5(
    password_autotrade.encode('utf-8')
).hexdigest()

auth_key_autotrade: str = hashlib.md5(
    (login_autotrade + password_md5_autotrade + salt).encode('utf-8')
).hexdigest()

# -------------------
# Формируем auth_key для abcp
# -------------------
password_md5_abcp: str = hashlib.md5(
    password_abcp.encode('utf-8')
).hexdigest()

# -------------------
# Заголовки HTTP-запросов
# -------------------
headers: dict = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


def remove_yesterday_file() -> None:
    """
    Удаляет файл Excel с результатами за вчерашний день
    в соответствии с save_excel().
    """

    directory = 'results'
    os.makedirs(directory, exist_ok=True)

    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%d-%m-%Y')

    filename = f'result_data_{date_str}.xlsx'
    filepath = os.path.join(directory, filename)

    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"[OK] Удалён файл: {filepath}")
    else:
        print(f"[INFO] Файл не найден: {filepath}")


def main() -> None:
    """
    Основная функция запуска.

    - Загружает артикулы Autotrade
    - Получает цены Autotrade
    - Загружает артикулы ABCP
    - Получает цены ABCP
    - Сохраняет результат в Excel
    """

    # ----------------------
    # Удаляем вчерашние файлы перед загрузкой
    # ----------------------
    remove_yesterday_file()

    try:

        # ---------- Autotrade ----------
        autotrade_file_path: str = "data/SAT autotrade.xlsx"
        autotrade_articles: list = load_article_info_from_excel(autotrade_file_path)

        autotrade_data: list = get_prices_autotrade(
            url=url_autotrade,
            headers=headers,
            auth_key=auth_key_autotrade,
            articles=autotrade_articles
        )

        save_excel(data=autotrade_data)

        # ---------- ABCP ----------
        abcp_file_path: str = "data/ОЕМ abcp.xlsx"
        abcp_articles: list = load_article_info_from_excel(abcp_file_path)

        abcp_data: list = get_prices_abcp(
            url=url_abcp,
            headers=headers,
            userlogin=login_abcp,
            userpsw=password_md5_abcp,
            articles=abcp_articles
        )

        save_excel(data=abcp_data)


    except Exception as ex:
        print(f'[ERROR] main: {ex}')
        return

        # ---------- Завершение ----------
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
