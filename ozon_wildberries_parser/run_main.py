from datetime import datetime

from parser import init_undetected_chromedriver, ozon_parser, wildberries_parser, workbook

start_time = datetime.now()


def main():
    """
    Точка входа: выбор парсинга Ozon, WB или обоих
    """
    try:
        value = input('Введите значение:\n1 - Ozon\n2 - Wildberries\n3 - Оба сайта\n')
    except Exception:
        raise Exception('Введено неправильное значение')

    match value:
        case '1':
            pages = int(input('Введите количество страниц Ozon: \n'))
            driver = init_undetected_chromedriver()
            try:
                print('Сбор данных Ozon')
                ozon_parser(driver, workbook, pages)
                print('Сбор данных Ozon завершен')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')
            finally:
                driver.close()
                driver.quit()

        case '2':
            pages = int(input('Введите количество страниц Wildberries: \n'))
            try:
                print('Сбор данных Wildberries')
                wildberries_parser(workbook, pages)
                print('Сбор данных Wildberries завершен')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')

        case '3':
            pages_ozon = int(input('Введите количество страниц Ozon: \n'))
            pages_wb = int(input('Введите количество страниц Wildberries: \n'))

            driver = init_undetected_chromedriver()
            try:
                print('Сбор данных Ozon')
                ozon_parser(driver, workbook, pages_ozon)
                print('Сбор данных Ozon завершен')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')
            finally:
                driver.close()
                driver.quit()

            try:
                print('Сбор данных Wildberries')
                wildberries_parser(workbook, pages_wb)
                print('Сбор данных Wildberries завершен')
            except Exception as ex:
                print(f'main: {ex}')
                input('Нажмите Enter, чтобы закрыть программу...')

        case _:
            print('Введено неправильное значение')

    execution_time = datetime.now() - start_time
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
