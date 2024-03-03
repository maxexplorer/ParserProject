import time
from random import randint

from undetected_chromedriver import Chrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# Функция получения количества страниц
def get_pages(html: str = None) -> int:
    try:
        soup = BeautifulSoup(html, 'lxml')

        pages = int(soup.find('div', class_='eo6').find_all('a')[-2].text)
    except Exception:
        pages = 1

    return pages


def get_data(file_path: str):
    # Открываем файл в формате .txt
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    # Создаем объект опций
    # options = ChromeOptions()
    # Включение фонового режима
    # options.add_argument('--headless')
    driver = Chrome()
    driver.maximize_window()
    driver.implicitly_wait(15)

    try:
        for url in urls_list[:1]:

            print(f'Обрабатывается: {url}')

            # try:
            #     driver.get(url=url)
            #     time.sleep(randint(3, 5))
            # except Exception as ex:
            #     print(f'{url}: {ex}')
            #     continue

            html = driver.page_source
            pages = get_pages(html=html)

            # for page in range(1, pages + 1):
            #     try:
            #         driver.get(url=url)
            #         time.sleep(randint(3, 5))
            #     except Exception as ex:
            #         print(f'{url}: {ex}')
            #         continue


            with open('index.html', 'r', encoding='utf-8') as file:
                html = file.read()

            soup = BeautifulSoup(html, 'lxml')





    except Exception as ex:
        print(ex)
    finally:
        time.sleep(10)
        driver.close()
        driver.quit()


def main():
    # get_data(file_path='data/urls_list_ozone.txt')
    get_pages()


if __name__ == '__main__':
    main()
