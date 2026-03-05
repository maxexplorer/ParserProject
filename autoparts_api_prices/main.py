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

from abcp import ABCPClient
from autotrade import AutotradeClient
from adeopro import AdeoproClient
from froza_client import FrozaClient

from config import (
    headers,
    file_structures,
    company_names,
    abcp_clients,
    autotrade_clients,
    adeopro_clients,
    froza_clients
)

from utils import (
    load_articles_from_data,
    load_prices_from_file,
    normalize,
    clear_prices_folder,
    process_paint_prices
)

from download_prices import download_prices

# Фиксируем время начала выполнения
start_time: datetime = datetime.now()


def main():
    # Очищаем папку prices перед обработкой
    clear_prices_folder()
    # Загружаем прайсы
    download_prices()

    try:
        # Получаем данные из исходного файла
        articles_dict, df, file_path = load_articles_from_data()

        if df is None:
            return

        # Общий словарь найденных данных
        found_data = {}

        # ---------- Autotrade (SAT) ----------
        for client_name, client_data in autotrade_clients.items():
            articles = articles_dict.get(client_name)
            if not articles:
                continue

            try:
                autotrade_client = AutotradeClient(
                    url=client_data['url'],
                    login=client_data['login'],
                    password=client_data['password'],
                    headers=headers
                )

                autotrade_data = autotrade_client.get_data(articles, client_name, interval=1.0)

                for item in autotrade_data:
                    article = item['Артикул']
                    found_data[(article, client_name)] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'name_manufacturer': item.get('Наименование производителя')

                    }
            except Exception as ex:
                print(f"[WARNING] Autotrade клиент '{client_name}' пропущен из-за ошибки: {ex}")
                continue

        # ---------- ABCP ----------
        for client_name, client_data in abcp_clients.items():
            articles = articles_dict.get(client_name)
            if not articles:
                continue

            try:
                # Создаем экземпляр клиента ABCP
                abcp_client = ABCPClient(
                    host=client_data['host'],
                    login=client_data['login'],
                    password=client_data['password'],
                    headers=headers
                )

                # Получаем данные
                abcp_data = abcp_client.get_data(articles, client_name, interval=1.0)

                # Обновляем найденные данные
                for item in abcp_data:
                    article = item['Артикул']
                    found_data[(article, client_name)] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'name_manufacturer': item.get('Наименование производителя')
                    }
            except Exception as ex:
                print(f"[WARNING] ABCP клиент '{client_name}' пропущен из-за ошибки: {ex}")
                continue

        # ---------- Adeopro ----------
        for client_name, client_data in adeopro_clients.items():
            articles = articles_dict.get(client_name)
            if not articles:
                continue

            try:
                adeopro_client = AdeoproClient(
                    url=client_data['url'],
                    login=client_data['login'],
                    password=client_data['password'],
                    headers=headers
                )

                adeopro_data = adeopro_client.get_data(articles, client_name, interval=1.0)

                for item in adeopro_data:
                    article = item['Артикул']
                    found_data[(article, client_name)] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'name_manufacturer': item.get('Наименование производителя')
                    }

            except Exception as ex:
                print(f"[WARNING] Adeopro клиент '{client_name}' пропущен из-за ошибки: {ex}")
                continue

        # ---------- Froza ----------
        for client_name, client_data in froza_clients.items():
            articles = articles_dict.get(client_name)
            if not articles:
                continue

            try:
                froza_client = FrozaClient(
                    url=client_data['url'],
                    login=client_data['login'],
                    password=client_data['password'],
                    headers=headers
                )

                froza_data = froza_client.get_data(articles, client_name, interval=1.0)

                for item in froza_data:
                    article = item['Артикул']
                    found_data[(article, client_name)] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'name_manufacturer': item.get('Наименование производителя')
                    }

            except Exception as ex:
                print(f"[WARNING] Froza клиент '{client_name}' ошибка: {ex}")
                continue

        # ------------------- Прочие прайсы -------------------
        price_files = glob.glob(os.path.join('prices', '*.xls*')) + glob.glob(os.path.join('prices', '*.csv'))

        # Обработка файлов prices
        for file_path_price in price_files:
            base_name = normalize(os.path.basename(file_path_price))

            try:
                article_col, price_col, quantity_col, name_col = file_structures.get(base_name,
                                                                                     (None, None, None, None))

                data = load_prices_from_file(
                    file_path_price,
                    article_col,
                    price_col,
                    quantity_col,
                    name_col
                )
            except Exception as ex:
                print(f"[WARNING] Прайс '{file_path_price}' пропущен из-за ошибки: {ex}")
                continue

            data_dict = {item['Артикул']: item for item in data}

            company_name = company_names.get(base_name)
            company_articles_data = articles_dict.get(company_name, [])

            company_articles = [
                article for article, _ in company_articles_data
            ]

            found_count = 0

            for article in company_articles:
                if article in data_dict:
                    item = data_dict[article]

                    found_data[(article, company_name)] = {
                        'price': item.get('Цена'),
                        'quantity': item.get('Количество'),
                        'name_manufacturer': item.get('Наименование производителя')
                    }

                    found_count += 1

            print(f'✅ Найдено {found_count} артикулов для {company_name}')

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
            manufacturer = str(row[df.columns[2]]).strip()

            key = (article, manufacturer)

            if key in found_data:
                df.at[idx, 'Цена'] = found_data[key]['price']
                df.at[idx, 'Количество'] = found_data[key]['quantity']
                df.at[idx, 'Наименование производителя'] = found_data[key]['name_manufacturer']

        # Сохраняем данные в исходный файл
        df.to_excel(file_path, index=False)

        # ------------------- ДОБАВЛЯЕМ ЦЕНЫ ПОКРАСКИ -------------------
        process_paint_prices(file_path)  # применяем покрасочные цены к файлу

    except Exception as ex:
        print(f'[ERROR] main: {ex}')
        return

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
