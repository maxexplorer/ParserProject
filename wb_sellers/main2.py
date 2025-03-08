import os
from datetime import datetime

from requests import Session

from pandas import DataFrame, ExcelWriter
from pandas import read_excel

start_time = datetime.now()


def get_inn(session: Session, headers: dict, id_seller: str) -> str:
    try:
        response = session.get(f'https://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/{id_seller}.json',
                                headers=headers)
        json_data = response.json()

    except Exception as ex:
        print(f'{id}: {ex}')

    try:
        inn = json_data.get('inn')
    except Exception:
        inn = None

    return inn



# Функция для получения данных о наличии товаров у продавца
def get_data_registration_date() -> None:
    df = read_excel("D:\\PycharmProjects\\ParserProject\\wb_sellers\\data\\wb_sellers.xlsx", sheet_name='Лист1')

    result_list = []
    batch_size = 100
    # Размер пакета для записи
    processed_count = 0  # Счетчик обработанных URL

    # Создаем сессию
    with Session() as session:
        for index, row in df.iterrows():
            url = row.iloc[0]
            id_seller = row.iloc[0].split('/')[-1]

            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': 'https://www.wildberries.ru/seller/177',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'x-client-name': 'site',
            }

            try:
                response = session.get(f'https://suppliers-shipment-2.wildberries.ru/api/v1/suppliers/{id_seller}',
                                       headers=headers, timeout=60)

                json_data = response.json()

            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            processed_count += 1
            print(f'Обработано URL: {processed_count}')  # Вывод количества обработанных URL


            registration_date = json_data.get('registrationDate')

            sale_item_quantity = json_data.get('saleItemQuantity')

            if registration_date and sale_item_quantity:
                if registration_date and sale_item_quantity:
                    reg_date = datetime.strptime(registration_date, '%Y-%m-%dT%H:%M:%SZ')
                    years_on_wb = (datetime.now() - reg_date).days // 365

                    if (years_on_wb == 1 and 1000 <= sale_item_quantity <= 4000) or \
                            (years_on_wb == 2 and 4001 <= sale_item_quantity <= 9000) or \
                            (years_on_wb >= 3 and sale_item_quantity >= 9001):

                        inn = get_inn(session=session, headers=headers, id_seller=id_seller)

                        result_list.append(
                            {
                                'Ссылка': url,
                                'ИНН': inn
                            }
                        )


            # Записываем данные в Excel каждые 100 URL
            if len(result_list) >= batch_size:
                save_excel(result_list)
                result_list.clear() # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_excel(result_list)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data.xlsx'

    if not os.path.exists(file_path):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='Sellers')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name='Sellers',
                           index=False)

    print(f'Данные сохранены в файл: {file_path}')

def main():
    get_data_products_wb()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
