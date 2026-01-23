# main.py
from parser import init_undetected_chromedriver, get_products_urls, get_unique_urls, get_products_data
from config import brand

URLS_FILE = 'data/product_urls_list.txt'

def main():
    driver = init_undetected_chromedriver(headless_mode=False)
    try:
        # 1) Получаем ссылки
        # get_products_urls(driver)
        # get_unique_urls(URLS_FILE)

        # 2) Читаем ссылки
        with open(URLS_FILE, 'r', encoding='utf-8') as f:
            product_urls = [line.strip() for line in f]

        # 3) Получаем данные и работаем с изображениями
        get_products_data(driver, product_urls, brand)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
