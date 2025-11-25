import os
import time
from datetime import datetime
import re

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()

exceptions_data = []


def init_undetected_chromedriver(headless_mode: bool = False):
    """
    Инициализирует браузер Chrome с использованием undetected_chromedriver.

    :param headless_mode: если True — браузер запустится без интерфейса.
    :return: объект WebDriver.
    """
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver = uc.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver


def scroll_and_get_html(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    prev_count = 0

    while True:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, ".developments-table .item")
            cur = len(items)

            if cur == prev_count and cur > 0:
                break

            prev_count = cur

            loadmore_btn = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button.btn-loadmore")
                )
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", loadmore_btn)
            driver.execute_script("arguments[0].click();", loadmore_btn)
            time.sleep(1.5)

        except:
            break

    return driver.page_source


def get_html(url, session):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    try:
        response = session.get(url=url, headers=headers)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def save_excel(data: list[dict]) -> None:
    """
    Сохраняет список данных в Excel-файл (results/result_data.xlsx).

    :param data: Список словарей с данными о товарах.
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    # Если файла нет — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    # Читаем существующие данные
    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    # Преобразуем новые данные в DataFrame
    new_df = DataFrame(data)

    # Дописываем новые строки в конец
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows + 1,
            header=(num_existing_rows == 0),
            sheet_name='Data',
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_data(driver, html, session):
    batch_size = 100
    result_data = []
    prices_data = []

    soup = BeautifulSoup(html, 'lxml')
    developer_items = soup.find('div', class_='developments-table').find_all('div', class_='item')
    for i in developer_items:
        try:
            developer_data = i.find_all('span')
        except Exception as ex:
            print(f'developer_data - {ex}')
            continue
        try:
            developer_name = i.find('a').get_text(strip=True)
        except Exception:
            developer_name = None
        if not developer_name:
            continue
        try:
            projects_count = developer_data[0].get_text(strip=True)
            if projects_count == '0':
                continue
        except Exception:
            projects_count = None
        try:
            min_price = developer_data[1].get_text(strip=True)
        except Exception:
            min_price = None
        try:
            max_price = developer_data[2].get_text(strip=True)
        except Exception:
            max_price = None
        try:
            avg_price = developer_data[3].get_text(strip=True)
        except Exception:
            avg_price = None
        try:
            developer_url = i.find('a').get('href')
            html = get_html(url=developer_url, session=session)
            soup = BeautifulSoup(html, 'lxml')
            project_items = soup.find('section', class_='developments-table single-developer-table').find_all('div',
                                                                                                              class_='item')
        except Exception as ex:
            print(f'url_developer - {ex}')
            continue
        for c in project_items:
            try:
                project_name = c.find('a').get_text(strip=True)
            except Exception:
                project_name = None
            if not project_name:
                continue
            try:
                property_type = c.find('span', class_='text-capitalize').get_text(strip=True)
            except Exception:
                property_type = None
            try:
                project_url = c.find('a').get('href')
                html = scroll_and_get_html(driver, project_url)
                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(f'url_project - {ex}')
                continue
            try:
                starting_price = soup.find('div', string=re.compile('Start price from')).find_next().get_text(
                    strip=True)
            except Exception as ex:
                starting_price = None
                exceptions_data.append(
                    (developer_url, project_url, ex)
                )
            try:
                price_per_sqft_from = soup.find('div', string=re.compile('Price Per Sqft from')).find_next().get_text(
                    strip=True)
            except Exception:
                price_per_sqft_from = None
            try:
                area_from = soup.find('div', string=re.compile('Area from')).find_next().get_text(strip=True)
            except Exception:
                area_from = None
            try:
                type = soup.find('div', string=re.compile('Type')).find_next().get_text(strip=True)
            except Exception:
                type = None
            try:
                bedrooms = soup.find('div', string=re.compile('Bedrooms')).find_next().get_text(strip=True)
            except Exception:
                bedrooms = None
            try:
                location = soup.find('div', string=re.compile('Location')).find_next().get_text(strip=True)
            except Exception:
                location = None
            try:
                completion = soup.find('div', string=re.compile('Est. Completion')).find_next().get_text(strip=True)
            except Exception:
                completion = None
            try:
                images_items = soup.find('div', class_='gallery-grid').find_all('div', class_='thickbox setThumbMe')
                images_urls = [image_item.find('img').get('data-lazy-src') for image_item in images_items]
            except Exception:
                images_urls = None

            result_data.append(
                {
                    'Developer name': developer_name,
                    'Projects count': projects_count,
                    'Min price': min_price,
                    'Max price': max_price,
                    'Avg price': avg_price,
                    'Project name': project_name,
                    'Property type': property_type,
                    'Starting price': starting_price,
                    'Price per sqft from': price_per_sqft_from,
                    'Area from': area_from,
                    'Type': type,
                    'Bedrooms': bedrooms,
                    'Location': location,
                    'Completion': completion,
                    'Developer link': developer_url,
                    'Project link': project_url,
                    'Images links': images_urls
                }
            )

            # Сохраняем партию данных в Excel
            if len(result_data) >= batch_size:
                save_excel(result_data)
                result_data.clear()

            try:
                price_range_items = soup.find('div', class_='prices-items').find_all('div', class_='item')
            except Exception:
                continue
            for item in price_range_items:
                try:
                    type_apartment = item.find('div', class_='first').get_text(strip=True)
                except Exception:
                    type_apartment = None
                try:
                    size_apartment = item.find('div', class_='second').find_all('p')[1].get_text(strip=True)
                except Exception:
                    size_apartment = None
                try:
                    price_apartment = item.find('div', class_='third').find_all('p')[1].get_text(strip=True)
                except Exception:
                    price_apartment = None

                prices_data.append(
                    {
                        'Project link': project_url,
                        'Type': type_apartment,
                        'Size': size_apartment,
                        'Price': price_apartment
                    }
                )

                # Сохраняем партию данных в Excel
                if len(prices_data) >= batch_size:
                    save_excel(result_data)
                    result_data.clear()

            print(f'Developer: {developer_name}, Project: {project_name}')

    # Сохраняем остатки
    if result_data:
        save_excel(result_data)
    # Сохраняем остаток
    if result_data:
        save_excel(result_data)


def main():
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        html = scroll_and_get_html(driver, url="https://dxboffplan.com/list-of-property-developers-in-uae/")

        with requests.Session() as session:
            get_data(driver, html, session)

    finally:
        driver.close()
        driver.quit()
    if len(exceptions_data) > 0:
        save_excel(data=exceptions_data)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
