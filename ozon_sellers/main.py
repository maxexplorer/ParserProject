import time
from datetime import datetime
import os
import re
from random import randint

from pandas import DataFrame, ExcelWriter
from pandas import read_excel

from new_undetected_chromedriver import Chrome as undetectedChrome
from new_undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

start_time = datetime.now()

url = "https://www.ozon.ru/seller/"


# Функция инициализации объекта chromedriver
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


# Функция получения данных товаров
def get_products_data(driver: undetectedChrome, url: str) -> None:
    result_list = []
    batch_size = 100

    for page in range(1, 1_000_000):
        page_url = f"{url}{page}"
        try:
            driver.get(url=page_url)

            # Ждём либо нужный элемент, либо текст об ошибке
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'header[data-widget="header"]')
                )
            )
            html = driver.page_source
        except Exception as ex:
            print(f"{page_url} - {ex}")
            continue

        if not html:
            print(f'not html: {page_url}')
            continue

        soup = BeautifulSoup(html, 'lxml')

        try:
            products_items = soup.find_all('div', class_='j3s_25 tile-root jx5_25 jx6_25')
        except Exception:
            products_items = []

        if not products_items:
            continue

        try:
            name = soup.find('span', class_='tsHeadline600Large').text.strip()
        except Exception:
            name = None

        try:
            button = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div/div[1]/div/div/div/div[1]/div/div/div[2]/button[3]')
            button.click()
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Понятно")]'))
            )
        except Exception:
            pass

        try:
            spans = driver.find_elements(By.XPATH, '//span[contains(@class, "tsBody400Small")]')
            for span in spans:
                match = re.search(r'\b\d{13}\b', span.text)
                if match:
                    psrn = match.group()
                    break
            else:
                psrn = None
        except Exception:
            psrn = None

        result_list.append(
            {
                'Ссылка': page_url,
                'Магазин': name,
                'ОГРН': psrn
            }
        )

        # Записываем данные в excel каждые batch_size
        if len(result_list) >= batch_size:
            save_excel(data=result_list)
            result_list.clear()  # Очищаем список для следующей партии

    # Записываем оставшиеся данные в Excel
    if result_list:
        save_excel(data=result_list)


# Функция для записи данных в формат xlsx
def save_excel(data: list) -> None:
    directory = 'results'

    os.makedirs(directory, exist_ok=True)

    file_path = f'{directory}/result_data.xlsx'

    if not os.path.exists(file_path):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='Sellers')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                           sheet_name='Sellers',
                           index=False)

    print(f'Данные сохранены в файл: {file_path}')


def main():
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        get_products_data(driver=driver, url=url)
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
