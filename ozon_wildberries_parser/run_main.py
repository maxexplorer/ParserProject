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
    article_info = load_article_info_from_excel()

    try:
        value = input('Введите значение:\n1 - Ozon\n2 - Wildberries\n3 - Оба сайта\n')
    except Exception:
        raise Exception('Введено неправильное значение')

    match value:
        case '1':
            pages = int(input('Введите количество страниц Ozon: \n'))
            try:
                print('Сбор данных Ozon...')
                update_prices_ozon(article_info=article_info)
                write_price_to_excel(article_info=article_info)
                driver = init_undetected_chromedriver()
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
                update_prices_wb(article_info=article_info)
                write_price_to_excel(article_info=article_info)
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
                update_prices_ozon(article_info=article_info)
                write_price_to_excel(article_info=article_info)
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
                update_prices_wb(article_info=article_info)
                write_price_to_excel(article_info=article_info)
                wildberries_parser(workbook=workbook, pages=pages_wb)
                print('Сбор данных Wildberries завершен.')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')

        case _:
            print('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
