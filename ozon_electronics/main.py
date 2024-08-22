from datetime import datetime

from undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions

from bs4 import BeautifulSoup

start_time = datetime.now()

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

# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
    except Exception as ex:
        print(ex)
        pages = 1

    return pages


def get_products_urls():
    pass

def get_products_data():
    pass


def main():

    driver = init_undetected_chromedriver(headless_mode=True)



    try:
        get_product_urls(driver=driver, category_data_list=category_data_list, processed_urls=processed_urls, brand=brand)
    except Exception as ex:
        print(f'main: {ex}')
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()

