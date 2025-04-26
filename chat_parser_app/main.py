# main.py

from bot import start_bot  # Импортируем запуск бота

if __name__ == "__main__":

    try:
        start_bot()
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")
