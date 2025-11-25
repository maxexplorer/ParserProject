import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from datetime import datetime
import re

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


start_time = datetime.now()
exceptions_list = []


# ---------------------------------------------------------------------
#  ИНИЦИАЛИЗАЦИЯ БРАУЗЕРА
# ---------------------------------------------------------------------
def init_undetected_chromedriver(headless_mode: bool = False):
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver = uc.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver


# ---------------------------------------------------------------------
#  УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ПРОКРУТКИ И ПОДГРУЗКИ "See More"
# ---------------------------------------------------------------------
def scroll_and_get_html(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    prev_count = 0

    while True:
        try:
            # Сколько элементов сейчас на странице
            items = driver.find_elements(By.CSS_SELECTOR, ".developments-table .item")
            cur_count = len(items)

            # Если количество не изменилось — конец списка
            if cur_count == prev_count and cur_count > 0:
                break

            prev_count = cur_count

            # Находим кнопку загрузки
            loadmore_btn = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-loadmore"))
            )

            # Листаем к кнопке
            driver.execute_script("arguments[0].scrollIntoView(true);", loadmore_btn)
            driver.execute_script("arguments[0].click();", loadmore_btn)

            time.sleep(2)

        except Exception:
            break

    return driver.page_source


# ---------------------------------------------------------------------
#  HTTP GET через requests
# ---------------------------------------------------------------------
def get_html(url, session):
    headers = {
        'Accept': '*/*',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }
    try:
        response = session.get(url=url, headers=headers)
        return response.text
    except Exception as ex:
        print(ex)


# ---------------------------------------------------------------------
#  ОСНОВНОЙ СБОР ДАННЫХ
# ---------------------------------------------------------------------
def get_data(html, session, driver):
    result_list = []
    price_range_list = []

    soup = BeautifulSoup(html, 'lxml')
    developer_items = soup.find('div', class_='developments-table').find_all('div', class_='item')

    for i in developer_items:

        # --- базовые данные о девелопере ---
        try:
            developer_data = i.find_all('span')
        except:
            continue

        try:
            developer_name = i.find('a').get_text(strip=True)
        except:
            continue

        try:
            projects_count = developer_data[0].get_text(strip=True)
            if projects_count == '0':
                continue
        except:
            projects_count = None

        try:
            min_price = developer_data[1].get_text(strip=True)
        except:
            min_price = None

        try:
            max_price = developer_data[2].get_text(strip=True)
        except:
            max_price = None

        try:
            avg_price = developer_data[3].get_text(strip=True)
        except:
            avg_price = None

        # --- ссылка на девелопера ---
        try:
            developer_url = i.find('a').get('href')
        except:
            continue

        # ---------------------------------------------------------------------
        #  ПОЛНАЯ ПОДГРУЗКА СТРАНИЦЫ ДЕВЕЛОПЕРА В SELENIUM
        # ---------------------------------------------------------------------
        try:
            dev_html = scroll_and_get_html(driver, developer_url)
            soup_dev = BeautifulSoup(dev_html, 'lxml')
            project_items = soup_dev.find('section', class_='developments-table single-developer-table').find_all('div', class_='item')
        except Exception as ex:
            print(f'url_developer - {ex}')
            continue

        # ---------------------------------------------------------------------
        #  ПРОЕКТЫ ЭТОГО ДЕВЕЛОПЕРА
        # ---------------------------------------------------------------------
        for c in project_items:

            try:
                project_name = c.find('a').get_text(strip=True)
            except:
                continue

            try:
                property_type = c.find('span', class_='text-capitalize').get_text(strip=True)
            except:
                property_type = None

            try:
                project_url = c.find('a').get('href')
                html_project = get_html(project_url, session)
                soup_proj = BeautifulSoup(html_project, 'lxml')
            except:
                continue

            # --- данные проекта ---
            try:
                starting_price = soup_proj.find('div', string=re.compile('Start price from')).find_next().get_text(strip=True)
            except Exception as ex:
                starting_price = None
                exceptions_list.append((developer_url, project_url, ex))

            try:
                price_per_sqft_from = soup_proj.find('div', string=re.compile('Price Per Sqft from')).find_next().get_text(strip=True)
            except:
                price_per_sqft_from = None

            try:
                area_from = soup_proj.find('div', string=re.compile('Area from')).find_next().get_text(strip=True)
            except:
                area_from = None

            try:
                type_ = soup_proj.find('div', string=re.compile('Type')).find_next().get_text(strip=True)
            except:
                type_ = None

            try:
                bedrooms = soup_proj.find('div', string=re.compile('Bedrooms')).find_next().get_text(strip=True)
            except:
                bedrooms = None

            try:
                location = soup_proj.find('div', string=re.compile('Location')).find_next().get_text(strip=True)
            except:
                location = None

            try:
                completion = soup_proj.find('div', string=re.compile('Est. Completion')).find_next().get_text(strip=True)
            except:
                completion = None

            try:
                images_items = soup_proj.find('div', class_='gallery-grid').find_all('div', class_='thickbox setThumbMe')
                images_urls = [img.find('img').get('data-lazy-src') for img in images_items]
            except:
                images_urls = None

            result_list.append(
                (
                    developer_name,
                    projects_count,
                    min_price,
                    max_price,
                    avg_price,
                    project_name,
                    property_type,
                    starting_price,
                    price_per_sqft_from,
                    area_from,
                    type_,
                    bedrooms,
                    location,
                    completion,
                    developer_url,
                    project_url,
                    images_urls
                )
            )

            # ---------------------------------------------------------------------
            #  ЦЕНЫ ПО ТИПАМ КВАРТИР
            # ---------------------------------------------------------------------
            try:
                price_range_items = soup_proj.find('div', class_='prices-items').find_all('div', class_='item')
            except:
                price_range_items = []

            for item in price_range_items:
                try:
                    type_apartment = item.find('div', class_='first').get_text(strip=True)
                except:
                    type_apartment = None

                try:
                    size_apartment = item.find('div', class_='second').find_all('p')[1].get_text(strip=True)
                except:
                    size_apartment = None

                try:
                    price_apartment = item.find('div', class_='third').find_all('p')[1].get_text(strip=True)
                except:
                    price_apartment = None

                price_range_list.append(
                    (
                        project_url,
                        type_apartment,
                        size_apartment,
                        price_apartment
                    )
                )

            print(f"Developer: {developer_name} | Project: {project_name}")

    return result_list, price_range_list


# ---------------------------------------------------------------------
#  СОХРАНЕНИЕ CSV
# ---------------------------------------------------------------------
def save_csv_data(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_dxboffplan_1.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow((
            'Developer name','Projects count','Min price','Max price','Avg price',
            'Project name','Property type','Starting price','Price per sqft from',
            'Area from','Type','Bedrooms','Location','Completion','Developer link',
            'Project link','Images links'
        ))

    with open('data/data_dxboffplan_1.csv', 'a', encoding='utf-8', newline='') as file:
        csv.writer(file).writerows(data)


def save_csv_price(price):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/price_dxboffplan.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(('Project link','Type','Size','Price'))

    with open('data/price_dxboffplan.csv', 'a', encoding='utf-8', newline='') as file:
        csv.writer(file).writerows(price)


# ---------------------------------------------------------------------
#  MAIN
# ---------------------------------------------------------------------
def main():
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        # Загружаем главную страницу всех девелоперов
        html = scroll_and_get_html(driver,
                                   "https://dxboffplan.com/list-of-property-developers-in-uae/")
    finally:
        pass  # НЕ закрываем драйвер — он нужен в get_data!

    with requests.Session() as session:
        data, price = get_data(html, session, driver)

    driver.quit()

    save_csv_data(data)
    save_csv_price(price)

    if exceptions_list:
        with open('data/exceptions_list.csv', 'w', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(exceptions_list)

    print("Сбор данных завершён!")
    print("Время работы:", datetime.now() - start_time)


if __name__ == '__main__':
    main()
