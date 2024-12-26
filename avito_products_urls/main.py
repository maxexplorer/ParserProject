import time
from random import randint

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By


# Создаём объект undetected_chromedriver
def init_undetected_chromedriver(headless_mode=False):
    if headless_mode:
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = undetectedChrome(options=options)
        driver.implicitly_wait(15)
    else:
        driver = undetectedChrome()
        driver.maximize_window()
        driver.implicitly_wait(15)
    return driver

# Функция получения ссылок на товары
def get_products_urls(driver: undetectedChrome, num_passes: int) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/data.txt'

    with open(file_path, 'r', encoding='utf-8') as file:
        sellers_urls = [line.strip() for line in file.readlines()]

    for seller_url in sellers_urls:
        products_urls_set = set()

        try:
            driver.get(url=seller_url)
            time.sleep(3)  # Дождаться загрузки страницы
        except Exception as ex:
            print(f"{seller_url} - {ex}")
            continue

        # Пролистываем страницу до конца
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Сохраняем текущие ссылки
            urls_items = driver.find_elements(By.CSS_SELECTOR, 'a[itemprop="url"]')
            for url_item in urls_items:
                try:
                    product_url = url_item.get_attribute("href")
                except Exception as ex:
                    print(ex)
                    continue

                products_urls_set.add(product_url)

            print(f'Получено {len(products_urls_set)} ссылок')

            # Скроллим вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Ждём загрузки новых товаров

            # Проверяем, изменился ли размер страницы
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # Новых товаров не появилось
                break
            last_height = new_height

        products_urls_list = list(products_urls_set)

        print(f'Всего получено ссылок: {len(products_urls_list)}')

        get_products_cards(driver=driver, products_urls_list=products_urls_list, num_passes=num_passes)

# Функция получения карточки товара
def get_products_cards(driver: undetectedChrome, products_urls_list: list, num_passes: int) -> None:
    for pass_num in range(num_passes):
        print(f"Прохождение: {pass_num + 1}/{num_passes}")
        for i, product_url in enumerate(products_urls_list, 1):
            try:
                driver.get(url=product_url)

                time.sleep(randint(1, 3))

            except Exception as ex:
                print(f'{product_url}: {ex}')
                continue

            print(f'Обработано: {i}/{len(products_urls_list)}')


def main():
    # Запрашиваем у пользователя количество проходов по ссылкам
    num_passes = int(input("Введите количество проходов по ссылкам: "))

    driver = init_undetected_chromedriver(headless_mode=True)

    try:
        get_products_urls(driver=driver, num_passes=num_passes)
    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
