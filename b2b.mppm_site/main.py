import time
from datetime import datetime
import os
import json
from random import randint

from requests import Session
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter, read_excel

from configs import headers

start_time = datetime.now()


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            raise f'status_code: {response.status_code}'

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем ссылки статей
def get_product_urls(headers: dict) -> None:
    products_urls_list = []

    with Session() as session:
        try:
            time.sleep(1)
            url = f"https://b2b.mppm.ru/catalog/"
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f"{url} - {ex}")

        soup = BeautifulSoup(html, 'lxml')

        try:
            urls_items = soup.find('div', class_='alphabet__main').find_all('div', class_='alphabet__link')
        except Exception as ex:
            print(f'urls_items: {ex}')

        for i, url_item in enumerate(urls_items, 1):
            try:
                product_url_short = url_item.find('a').get('href')
                product_url = f"https://b2b.mppm.ru{product_url_short}"
                products_urls_list.append(product_url)
            except Exception as ex:
                print(f'product_url: {ex}')
                continue

            print(f'Обработано: {i} url!')

    if not os.path.exists('data'):
        os.makedirs(f'data')

    with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
        print(*products_urls_list, file=file, sep='\n')


# Получаем данные о продуктах
def get_products_data(file_path: str, headers: dict, ) -> None:
    with open(file_path, 'r', encoding='utf-8') as file:
        products_urls_list = [line.strip() for line in file.readlines()]

    count = len(products_urls_list)
    title_plants_data = list()
    suppliers_data = list()
    suppliers_processed = list()

    # Размер пакета для записи
    batch_size = 100
    # Счетчик обработанных URL
    processed_count = 0

    with Session() as session:
        for j, product_url in enumerate(products_urls_list, 1):
            try:
                time.sleep(randint(1, 3))
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f'{product_url} - {ex}')
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                title_ru = soup.find('h1').text.strip()
            except Exception:
                print(f'not title: {product_url}')
                continue

            try:
                title_lat = soup.find('span', class_='catalog-top__latin').text.strip()
            except Exception:
                title_lat = None

            title_plants_data.append((title_ru, title_lat))

            # Поиск скрипта с данными
            script_tag = soup.find("script", string=lambda t: t and "window.dataSearchList" in t)

            if script_tag:
                # Извлечение текста и очистка
                script_content = script_tag.string.strip()
                json_str = script_content.split("=", 1)[-1].strip().rstrip(";").rstrip("|| []")
                data = json.loads(json_str)  # Преобразование в Python-объект

                # Доступ к region и address для всех поставщиков
                suppliers = data.get('filter', {}).get('supplier', {})
                try:
                    for supplier_id, supplier_info in suppliers.items():
                        title = supplier_info.get('title')
                        region = supplier_info.get('region')
                        address = supplier_info.get('address')

                        if title in suppliers_processed:
                            continue

                        suppliers_processed.append(title)

                        suppliers_data.append(
                            (
                                title,
                                region,
                                address,
                            )
                        )
                except Exception as ex:
                    print(f'suppliers: {product_url} - {ex}')

            processed_count += 1
            print(f'Обработано товаров: {j}/{count}')

            # Записываем данные в Excel каждые 100 URL
            if len(title_plants_data) >= batch_size:
                save_excel(data=title_plants_data, sheet_name='Plants')
                save_excel(data=suppliers_data, sheet_name='Suppliers')
                title_plants_data.clear()  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if title_plants_data:
        save_excel(data=title_plants_data, sheet_name='Plants')
        save_excel(data=suppliers_data, sheet_name='Suppliers')


# Функция для записи данных в формат xlsx
def save_excel(data: list | set, sheet_name: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data.xlsx'

    if not os.path.exists(file_path):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Получаем все листы из файла
    existing_sheets = read_excel(file_path, sheet_name=None)
    if sheet_name not in existing_sheets:
        # Если файл существует, добавляем пустой лист
        with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name=sheet_name)
    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name=sheet_name, index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    # get_product_urls(headers=headers)

    get_products_data(file_path='data/products_urls_list.txt', headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
