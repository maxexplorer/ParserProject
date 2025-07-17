# main.py

from datetime import datetime

from parser import (
    init_undetected_chromedriver,
    ozon_parser,
    wildberries_parser,
    workbook
)

from update_price import (
    update_prices_ozon,
    update_prices_wb,
    write_price_to_excel,
    load_article_info_from_excel
)

from analytics_report import (
    get_ozon_orders_report,
    get_wb_orders_report,
    write_analytics_to_excel
)

def main():
    while True:
        print(
            '\nВыберите действие:\n'
            '1 - Собрать данные Ozon\n'
            '2 - Собрать данные Wildberries\n'
            '3 - Собрать данные Ozon и Wildberries\n'
            '4 - Обновить цены Ozon\n'
            '5 - Обновить цены Wildberries\n'
            '6 - Обновить цены Ozon и Wildberries\n'
            '7 - Получить отчет заказов Ozon за месяц\n'
            '8 - Получить отчет заказов Ozon за неделю\n'
            '9 - Получить отчет заказов WB за месяц\n'
            '10 - Получить отчет заказов WB за неделю\n'
            '0 - Выход\n'
        )
        value = input('Введите значение: ').strip()
        start_time = datetime.now()

        try:
            match value:
                case '0':
                    print('Выход из программы.')
                    break

                case '1':
                    pages = int(input('Введите количество страниц Ozon: '))
                    driver = init_undetected_chromedriver()
                    try:
                        print('Сбор данных Ozon...')
                        ozon_parser(driver=driver, workbook=workbook, pages=pages)
                        print('✅ Сбор данных Ozon завершен.')
                    finally:
                        driver.quit()

                case '2':
                    pages = int(input('Введите количество страниц Wildberries: '))
                    print('Сбор данных Wildberries...')
                    wildberries_parser(workbook=workbook, pages=pages)
                    print('✅ Сбор данных Wildberries завершен.')

                case '3':
                    pages_ozon = int(input('Введите количество страниц Ozon: '))
                    pages_wb = int(input('Введите количество страниц Wildberries: '))
                    driver = init_undetected_chromedriver()
                    try:
                        print('Сбор данных Ozon...')
                        ozon_parser(driver=driver, workbook=workbook, pages=pages_ozon)
                        print('✅ Сбор данных Ozon завершен.')
                    finally:
                        driver.quit()
                    print('Сбор данных Wildberries...')
                    wildberries_parser(workbook=workbook, pages=pages_wb)
                    print('✅ Сбор данных Wildberries завершен.')

                case '4':
                    print('Обновление цен Ozon...')
                    article_info = load_article_info_from_excel(sheet_name='ОЗОН')
                    current_prices = update_prices_ozon(article_info=article_info)
                    write_price_to_excel(current_prices=current_prices, marketplace='ОЗОН')
                    print('✅ Цены Ozon обновлены и сохранены.')

                case '5':
                    print('Обновление цен Wildberries...')
                    article_info = load_article_info_from_excel(sheet_name='ВБ')
                    current_prices = update_prices_wb(article_info=article_info)
                    write_price_to_excel(current_prices=current_prices, marketplace='ВБ')
                    print('✅ Цены Wildberries обновлены и сохранены.')

                case '6':
                    print('Обновление цен Ozon...')
                    article_info_ozon = load_article_info_from_excel(sheet_name='ОЗОН')
                    current_prices_ozon = update_prices_ozon(article_info=article_info_ozon)
                    write_price_to_excel(current_prices=current_prices_ozon, marketplace='ОЗОН')
                    print('✅ Цены Ozon обновлены и сохранены.')

                    print('Обновление цен Wildberries...')
                    article_info_wb = load_article_info_from_excel(sheet_name='ВБ')
                    current_prices_wb = update_prices_wb(article_info=article_info_wb)
                    write_price_to_excel(current_prices=current_prices_wb, marketplace='ВБ')
                    print('✅ Цены Wildberries обновлены и сохранены.')

                case '7':
                    print('Получение отчета Ozon за месяц...')
                    ozon_orders = get_ozon_orders_report(period='month')
                    write_analytics_to_excel(analytics_data=ozon_orders, marketplace='ОЗОН', period='month')
                    print('✅ Отчет Ozon за месяц собран и записан.')

                case '8':
                    print('Получение отчета Ozon за неделю...')
                    ozon_orders = get_ozon_orders_report(period='week')
                    write_analytics_to_excel(analytics_data=ozon_orders, marketplace='ОЗОН', period='week')
                    print('✅ Отчет Ozon за неделю собран и записан.')

                case '9':
                    print('Получение отчета WB за месяц...')
                    wb_orders = get_wb_orders_report(period='month')
                    write_analytics_to_excel(analytics_data=wb_orders, marketplace='ВБ', period='month')
                    print('✅ Отчет WB за месяц собран и записан.')

                case '10':
                    print('Получение отчета WB за неделю...')
                    wb_orders = get_wb_orders_report(period='week')
                    write_analytics_to_excel(analytics_data=wb_orders, marketplace='ВБ', period='week')
                    print('✅ Отчет WB за неделю собран и записан.')

                case _:
                    print('❌ Неверный выбор. Попробуйте снова.')

        except Exception as ex:
            print(f'❌ Ошибка: {ex}')
            input("Нажмите Enter, чтобы закрыть программу...")

        execution_time = datetime.now() - start_time
        print(f'⏱️ Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
