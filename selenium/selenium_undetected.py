from undetected_chromedriver import Chrome
import time


def undetected_chromdriver():
    driver = Chrome()
    driver.maximize_window()

    driver = Chrome()
    driver.maximize_window()

    try:
        driver.get(url="https://ozon.ru/t/jYDXY4o")
        time.sleep(15)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():
    undetected_chromdriver()


if __name__ == '__main__':
    main()
