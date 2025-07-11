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

start_time = datetime.now()

def main():
    try:
        value = input('Введите значение:\n'
                      '1 - Собрать данные Ozon\n'
                      '2 - Собрать данные Wildberries\n'
                      '3 - Собрать данные Ozon и Wildberries\n'
                      '4 - Обновить цены Ozon\n'
                      '5 - Обновить цены Wildberries\n'
                      '6 - Обновить цены Ozon и Wildberries\n')
    except Exception:
        raise Exception('Введено неправильное значение')

    match value:
        case '1':
            pages = int(input('Введите количество страниц Ozon: \n'))
            driver = init_undetected_chromedriver()
            try:
                print('Сбор данных Ozon...')
                ozon_parser(driver=driver, workbook=workbook, pages=pages)
                print('Сбор данных Ozon завершен.')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')
            finally:
                driver.close()
                driver.quit()

        case '2':
            pages = int(input('Введите количество страниц Wildberries: \n'))
            try:
                print('Сбор данных Wildberries...')
                wildberries_parser(workbook=workbook, pages=pages)
                print('Сбор данных Wildberries завершен.')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')

        case '3':
            pages_ozon = int(input('Введите количество страниц Ozon: \n'))
            pages_wb = int(input('Введите количество страниц Wildberries: \n'))
            driver = init_undetected_chromedriver()
            try:
                print('Сбор данных Ozon...')
                ozon_parser(driver=driver, workbook=workbook, pages=pages_ozon)
                print('Сбор данных Ozon завершен.')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')
            finally:
                driver.close()
                driver.quit()
            try:
                print('Сбор данных Wildberries...')
                wildberries_parser(workbook=workbook, pages=pages_wb)
                print('Сбор данных Wildberries завершен.')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')

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

        case _:
            print('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')

if __name__ == '__main__':
    main()
