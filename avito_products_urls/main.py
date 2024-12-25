import time

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By

from data.data import sellers_urls


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


def get_products_urls(driver: undetectedChrome, sellers_urls: list) -> list:
    for seller_url in sellers_urls:
        products_urls_set = set()

        try:
            driver.get(seller_url)
            time.sleep(3)  # Дождаться загрузки страницы
        except Exception as ex:
            print(f"{seller_url} - {ex}")
            continue

        # Пролистываем страницу до конца
        last_height = driver.execute_script("return document.body.scrollHeight")


        while True:
            # Сохраняем текущие ссылки
            items = driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]")  # Задайте точный XPath
            for item in items:
                products_urls_set.add(item.get_attribute("href"))

            # Скроллим вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Ждём загрузки новых товаров

            # Проверяем, изменился ли размер страницы
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Новых товаров не появилось
                break
            last_height = new_height

    print(f"Всего найдено товаров: {len(products_urls_set)}")
    return list(products_urls_set)


def main():
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        get_products_urls(driver=driver, sellers_urls=sellers_urls)
    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
