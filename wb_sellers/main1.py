import os
from datetime import datetime

from requests import Session

from pandas import DataFrame, ExcelWriter
from pandas import read_excel

start_time = datetime.now()

df = read_excel("D:\\PycharmProjects\\ParserProject\\wb_sellers\\results\\result_data.xlsx", sheet_name='Sellers')


# Функция для получения данных о наличии товаров у продавца
def get_data_products_wb() -> None:
    result_list = []
    batch_size = 100
    # Размер пакета для записи
    processed_count = 0  # Счетчик обработанных URL

    # Создаем сессию
    with Session() as session:
        for index, row in df.iterrows():
            url = row[0]
            id_seller = row[0].split('/')[-1]

            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': 'https://www.wildberries.ru/seller/3999481',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'x-client-name': 'site',
            }

            try:
                response = session.get(f'https://suppliers-shipment.wildberries.ru/api/v1/suppliers/{id_seller}',
                                       headers=headers, timeout=60)

                if response.status_code != 200:
                    print(f'status_code: {response.status_code}')
                    if not os.path.exists('data'):
                        os.makedirs('data')
                    with open('data/exceptions_list.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{url}\n')
                    continue

                json_data = response.json()

            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            processed_count += 1
            print(f'Обработано URL: {processed_count}')  # Вывод количества обработанных URL

            try:
                sale_item_quantity = json_data['saleItemQuantity']
                if sale_item_quantity >= 1000:
                    result_list.append(url)
            except Exception as ex:
                print(f'json_data: {url} - {ex}')
                continue

            # Записываем данные в Excel каждые 100 URL
            if len(result_list) >= batch_size:
                save_excel(result_list)
                result_list = []  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_excel(result_list)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists(f'results/result_data_over_1000.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(f'results/result_data_over_1000.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    # Загружаем данные из файла
    df = read_excel(f'results/result_data_over_1000.xlsx', sheet_name='Sellers')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(f'results/result_data_over_1000.xlsx', mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name='Sellers',
                           index=False)

    print(f'Данные сохранены в файл "result_data.xlsx"')


def main():
    get_data_products_wb()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
