# main.py

from process_orders import run_order_process
from calculate_profit import run_product_prices
from deactivate_actions import run_deactivate_actions
from product_report import run_product_report


def main():
    try:
        while True:
            print('\n📋 Выберите действие:')
            print('1 - Получить необработанные заказы')
            print('2 - Получить остатки на расходы')
            print('3 - Удалить товары из акции')
            print('4 - Скачать отчёт по товарам')  # Новая опция
            print('0 - Выход')

            choice = input('Введите номер действия: ').strip()

            match choice:
                case '1':
                    run_order_process()
                case '2':
                    run_product_prices()
                case '3':
                    run_deactivate_actions()
                case '4':
                    run_product_report()  # Новый вызов
                case '0':
                    print("👋 Выход из программы.")
                    break
                case _:
                    print("❗ Неверный выбор. Попробуйте снова.")
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")


if __name__ == '__main__':
    main()
