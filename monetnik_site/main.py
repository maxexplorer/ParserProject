import os
import time
from datetime import datetime
import json

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str | None:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


def get_products_data(headers: dict) -> list[dict]:
    batch_size = 1000
    result_data = []

    with Session() as session:
        for page in range(1, 1147):
            products_urls_list = []

            page_url = f"https://www.monetnik.ru/monety/page.{page}/"

            try:
                time.sleep(1)
                html = get_html(url=page_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{page_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                product_items = soup.find_all('div', class_='product__card--quick track-merchandising')
            except Exception as ex:
                print(f'product_card_info: {page_url} - {ex}')
                continue

            for product_item in product_items:
                try:
                    product_name = product_item.find('span', class_='product__card-name').get_text(strip=True)
                except Exception:
                    product_name = None

                try:
                    price = ''.join(filter(lambda x: x.isdigit(),
                                           product_item.find('div', class_='product__card-prices').next.get_text(
                                               strip=True)))
                except Exception:
                    price = None

                try:
                    old_price = ''.join(
                        filter(lambda x: x.isdigit(), product_item.find('span', class_='strike').get_text(strip=True)))
                except Exception:
                    old_price = None

                try:
                    product_url = product_item.find('a', class_='absolute-link').get('href')
                except Exception:
                    product_url = None

                if product_url:
                    products_urls_list.append(product_url)

                result_data.append(
                    {
                        'Name': product_name,
                        'Price': price,
                        'Old price': old_price,
                    }
                )

            directory = 'data'

            os.makedirs(directory, exist_ok=True)

            with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
                print(*products_urls_list, file=file, sep='\n')

            print(f'Обработано: {page}')

            if len(result_data) >= batch_size:
                save_excel(result_data)
                result_data.clear()

        if result_data:
            save_excel(result_data)

    return result_data


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Data', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main():
    result_data = get_products_data(headers=headers)
    save_excel(data=result_data)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
