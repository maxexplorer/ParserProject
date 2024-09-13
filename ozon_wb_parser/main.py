from datetime import datetime

from ozon import get_urls_rating_feedbacks
from ozon import get_data_products_ozon
from ozon import save_excel_ozon
from wildberries import get_data_products_wb
from wildberries import save_excel_wb

start_time = datetime.now()


def main():
    value = input('Введите значение:\n1 - ozon\n2 - Wildberries\n3 - Оба сайта\n')

    if value == '1':
        print('Сбор данных Ozon')
        product_data = get_urls_rating_feedbacks(file_path='data/urls_list_ozon.txt')
        ozon_data = get_data_products_ozon(product_data=product_data)
        save_excel_ozon(data=ozon_data)
        print('Сбор данных Ozon завершен')
    elif value == '2':
        print('Сбор данных Wildberries')
        wb_data = get_data_products_wb(file_path='data/urls_list_wb.txt')
        save_excel_wb(data=wb_data)
        print('Сбор данных Wildberries завершен')
    elif value == '3':
        print('Сбор данных Ozon')
        product_data = get_urls_rating_feedbacks(file_path='data/urls_list_ozon.txt')
        ozon_data = get_data_products_ozon(product_data=product_data)
        save_excel_ozon(data=ozon_data)
        print('Сбор данных Ozon завершен')

        print('Сбор данных Wildberries')
        wb_data = get_data_products_wb(file_path='data/urls_list_wb.txt')
        save_excel_wb(data=wb_data)
        print('Сбор данных Wildberries завершен')
    else:
        print('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
