# main.py
from process_orders import run_order_process
from calculate_profit import run_product_prices


def main():
    try:
        while True:
            print("\n📋 Выберите действие:")
            print("1 - Получить заказы")
            print("2 - Получить чистую прибыль")
            print("0 - Выход")
            choice = input("Введите номер действия: ").strip()

            if choice == '1':
                run_order_process()
            elif choice == '2':
                run_product_prices()
            elif choice == '0':
                print("👋 Выход из программы.")
                break
            else:
                print("❗ Неверный выбор. Попробуйте снова.")
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")


if __name__ == '__main__':
    main()
