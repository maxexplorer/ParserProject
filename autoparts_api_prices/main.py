# main.py

"""
Точка входа приложения.

Скрипт:
- Загружает артикулы из Excel
- Получает цены из Autotrade и ABCP
- Сохраняет результаты в Excel
"""

import os
from datetime import datetime
import glob

from autotrade import get_prices_autotrade
from abcp import get_prices_abcp

from config import (
    headers,
    url_autotrade,
    url_abcp,
    auth_key_autotrade,
    password_md5_abcp,
    login_abcp,
    file_structures,
    company_names
)

from utils import (
    load_articles_from_data,
    load_prices_from_file,
    normalize,
    remove_yesterday_file,
    clear_prices_folder,
    save_excel
)

# Фиксируем время начала выполнения
start_time: datetime = datetime.now()


def main():
    # remove_yesterday_file()

    try:
        # Получаем данные из исходного файла
        articles_dict, df, file_path = load_articles_from_data()

        if df is None:
            return

        # Общий словарь найденных данных
        found_data = {}

        # ---------- Autotrade (SAT) ----------
        # if articles_dict.get('ООО "АТМ"'):
        #     autotrade_data = get_prices_autotrade(
        #         url=url_autotrade,
        #         headers=headers,
        #         auth_key=auth_key_autotrade,
        #         articles=articles_dict.get('ООО "АТМ"')
        #     )
        #     save_excel(autotrade_data)
        #
        #     for item in autotrade_data:
        #         found_data[item['Артикул']] = {
        #             'price': item.get('Цена'),
        #             'source': 'Autotrade'
        #         }

        # ---------- ABCP (OEM) ----------
        # if articles_dict.get('ИП Кунаков Ю.В.'):
        #     abcp_data = get_prices_abcp(
        #         url=url_abcp,
        #         headers=headers,
        #         userlogin=login_abcp,
        #         userpsw=password_md5_abcp,
        #         articles=articles_dict.get('ИП Кунаков Ю.В.')
        #     )
        #     save_excel(abcp_data)
        #
        #     for item in abcp_data:
        #         found_data[item['Артикул']] = {
        #             'price': item.get('Цена'),
        #             'source': 'ABCP'
        #         }

        # ------------------- Прочие прайсы -------------------
        price_files = glob.glob(os.path.join('prices', '*.xls*')) + glob.glob(os.path.join('prices', '*.csv'))

        # Обработка файлов prices
        for file_path_price in price_files:
            base_name = normalize(os.path.basename(file_path_price))

            article_col, price_col, quantity_col, name_col = file_structures.get(base_name, (None, None, None))

            data = load_prices_from_file(
                file_path_price,
                article_col,
                price_col,
                quantity_col,
                name_col
            )

            filtered_data = []

            for item in data:
                article = item['Артикул']
                company = company_names.get(base_name)
                company_articles = articles_dict.get(company, {})

                if article in company_articles:
                    filtered_data.append(item)

                    # Добавляем в общий словарь
                    found_data[article] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'manufacturer_name': item.get('Наименование производителя')
                    }

            if filtered_data:
                save_excel(filtered_data, file_name='result_data')

        # ------------------- ОБНОВЛЯЕМ ИСХОДНЫЙ EXCEL -------------------

        # добавляем колонки если их нет
        if 'Цена' not in df.columns:
            df['Цена'] = ''
        if 'Количество' not in df.columns:
            df['Количество'] = ''
        if 'Наименование производителя' not in df.columns:
            df['Наименование производителя'] = ''

        for idx, row in df.iterrows():
            article = str(row[df.columns[5]]).strip()

            if article in found_data:
                df.at[idx, 'Цена'] = found_data[article]['price']
                df.at[idx, 'Количество'] = found_data[article]['quantity']
                df.at[idx, 'Наименование производителя'] = found_data[article]['manufacturer_name']

        # Сохраняем данные в исходный файл
        df.to_excel(file_path, index=False)

        # Очищаем папку prices после обработки
        # clear_prices_folder()

    except Exception as ex:
        print(f'[ERROR] main: {ex}')
        return

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
