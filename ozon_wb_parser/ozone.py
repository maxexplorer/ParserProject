import os
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

        print(f'Всего: {pages} страниц!')
    except Exception:
        pages = 1

    return pages

# Функция полученя ссылок всех продуктов продавца
def get_urls(file_path: str) -> list:
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

    product_urls_list = []

    try:
        for url in urls_list[:1]:

            print(f'Обрабатывается: {url}')

            try:
                driver.get(url=url)
                time.sleep(randint(3, 5))
            except Exception as ex:
                print(f'{url}: {ex}')
                continue

            html = driver.page_source
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                try:
                    driver.get(url=f"{url}&page={page}")
                    time.sleep(randint(3, 5))
                except Exception as ex:
                    print(f'{url}: {ex}')
                    continue

                html = driver.page_source

                soup = BeautifulSoup(html, 'lxml')

                url_items = soup.find('div', class_='x6i').find_all('div', class_='iv4')

                print(f'Всего: {len(url_items)} продуктов на {page} странице!')

                for item in url_items:
                    try:
                        url_product = f"https://www.ozon.ru{item.find('a').get('href')}"
                    except Exception:
                        url_product = ''
                    product_urls_list.append(url_product)

                if not os.path.exists('data'):
                    os.makedirs('data')

                # with open('data/product_urls_list.txt', 'w', encoding='utf-8') as file:
                #     print(*product_urls_list, file=file, sep='\n')
        return product_urls_list

    except Exception as ex:
        print(ex)
    finally:
        time.sleep(10)
        driver.close()
        driver.quit()


def main():
    get_urls(file_path='data/urls_list_ozone.txt')
    # get_pages()


if __name__ == '__main__':
    main()
