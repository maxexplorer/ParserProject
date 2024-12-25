import time

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


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


def get_product_links(driver, seller_url):
    driver.get(seller_url)
    time.sleep(3)  # Дождаться загрузки страницы


    # Пролистываем страницу до конца
    last_height = driver.execute_script("return document.body.scrollHeight")
    product_links = set()

    while True:
        # Сохраняем текущие ссылки
        items = driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]")  # Задайте точный XPath
        for item in items:
            product_links.add(item.get_attribute("href"))

        # Скроллим вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Ждём загрузки новых товаров

        # Проверяем, изменился ли размер страницы
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Новых товаров не появилось
            break
        last_height = new_height

    print(f"Всего найдено товаров: {len(product_links)}")
    return list(product_links)


def main():
    driver = init_undetected_chromedriver(headless_mode=False)


if __name__ == '__main__':
    main()
