from datetime import datetime

from wildberries import get_data_products
from wildberries import save_excel_wb
from ozone import get_urls_rating_feedbacks
from ozone import get_data_products
from ozone import save_excel_ozone

start_time = datetime.now()


def main():
    value = input('Введите значение:\n1 - Ozone\n2 - Wildberries\n3 - Оба сайта\n')

    if value == '1':
        print('Сбор данных Ozone')
        product_data = get_urls_rating_feedbacks(file_path='data/urls_list_ozone.txt')
        ozone_data = get_data_products(product_data=product_data)
        save_excel_ozone(data=ozone_data)
        print('Сбор данных Ozone завершен')
    elif value == '2':
        print('Сбор данных Wildberries')
        wb_data = get_data_products(file_path='data/urls_list_wb.txt')
        save_excel_wb(data=wb_data)
        print('Сбор данных Wildberries завершен')
    elif value == '3':
        print('Сбор данных Ozone')
        product_data = get_urls_rating_feedbacks(file_path='data/urls_list_ozone.txt')
        ozone_data = get_data_products(product_data=product_data)
        save_excel_ozone(data=ozone_data)
        print('Сбор данных Ozone завершен')

        print('Сбор данных Wildberries')
        wb_data = get_data_products(file_path='data/urls_list_wb.txt')
        save_excel_wb(data=wb_data)
        print('Сбор данных Wildberries завершен')
    else:
        print('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')
