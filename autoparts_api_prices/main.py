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
from datetime import datetime
import glob

from autotrade import get_prices_autotrade
from abcp import get_prices_abcp

from config import login_autotrade, password_autotrade, login_abcp, password_abcp
from utils import load_articles_from_data, load_prices_from_file, normalize, remove_yesterday_file, clear_prices_folder, save_excel

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


def main():
    remove_yesterday_file()

    try:
        # ------------------- SAT и OEM -------------------
        articles_dict = load_articles_from_data()

        other_articles = {
            article for article, _ in articles_dict.get("OTHER", [])
        }

        not_found_articles = set(other_articles)

        # ---------- Autotrade (SAT) ----------
        # if articles_dict.get("SAT"):
        #     autotrade_data = get_prices_autotrade(
        #         url=url_autotrade,
        #         headers=headers,
        #         auth_key=auth_key_autotrade,
        #         articles=articles_dict["SAT"]
        #     )
        #     save_excel(autotrade_data)

        # ---------- ABCP (OEM) ----------
        # if articles_dict.get("OEM"):
        #     abcp_data = get_prices_abcp(
        #         url=url_abcp,
        #         headers=headers,
        #         userlogin=login_abcp,
        #         userpsw=password_md5_abcp,
        #         articles=articles_dict["OEM"]
        #     )
        #     save_excel(abcp_data)

        # ------------------- Прочие прайсы -------------------
        price_files = glob.glob(os.path.join("prices", "*.xls*"))

        # Для каждого файла указываем структуру: (article_col, price_col, start_row)
        file_structures = {
            'прайс опт': (2, 18),
            'прайс железо': (1, 6),
            'ПРАЙС АТБ': (0, 5),
            'прайс 1': (1, 3),
            'Прайс - ОПТ': (0, 8),
            'Наличие_Dominant': (1, 4),
            'price_atek': (1, 5),
            'Прайс': (1, 9)
        }

        # Обработка файлов prices
        for file_path in price_files:
            base_name = normalize(os.path.basename(file_path))
            col_article, col_price = 0, 1
            for key, val in file_structures.items():
                if normalize(key) in base_name:
                    col_article, col_price = val
                    break
            data = load_prices_from_file(
                file_path,
                col_article,
                col_price
            )

            filtered_data = []

            for item in data:
                article = item["Артикул"]
                if article in other_articles:
                    filtered_data.append(item)
                    not_found_articles.discard(article)

            if filtered_data:
                save_excel(filtered_data, file_name='result_data')

        if not_found_articles:
            unupdated_data = [
                {"Артикул": article}
                for article in not_found_articles
            ]

            save_excel(
                unupdated_data,
                file_name='unupdated_articles'
            )

        # Очищаем папку prices после обработки
        # clear_prices_folder()

    except Exception as ex:
        print(f"[ERROR] main: {ex}")
        return

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')

if __name__ == '__main__':
    main()

