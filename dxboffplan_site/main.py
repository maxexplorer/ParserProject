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

start_time: datetime = datetime.now()

exceptions_data: list[dict] = []


def init_undetected_chromedriver(headless_mode: bool = False) -> uc.Chrome:
    """
    Инициализирует браузер Chrome с использованием undetected_chromedriver.

    :param headless_mode: если True — браузер запустится без интерфейса.
    :return: объект WebDriver Chrome.
    """
    options: ChromeOptions = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver: uc.Chrome = uc.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.maximize_window()
    return driver


def scroll_and_get_html(driver: uc.Chrome, url: str) -> str:
    """
    Скроллит страницу с кнопкой 'Load More' до конца и возвращает HTML-код.

    :param driver: WebDriver Chrome.
    :param url: URL страницы для скролла.
    :return: HTML-код страницы.
    """
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


def get_html(url: str, session: requests.Session) -> str:
    """
    Получает HTML-страницу через requests с заголовками.

    :param url: URL страницы.
    :param session: объект requests.Session.
    :return: HTML-код страницы.
    """
    headers: dict[str, str] = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    try:
        response: requests.Response = session.get(url=url, headers=headers)
        return response.text
    except Exception as ex:
        print(ex)
        return ""


def save_excel(data: list[dict], file_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл с указанным именем.

    :param data: Список словарей с данными.
    :param file_name: Название файла Excel (без пути).
    """
    directory: str = 'results'
    file_path: str = f'{directory}/{file_name}'

    os.makedirs(directory, exist_ok=True)

    # Если файла нет — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    # Читаем существующие данные
    df_existing: DataFrame = read_excel(file_path, sheet_name='Data')
    num_existing_rows: int = len(df_existing.index)

    # Преобразуем новые данные в DataFrame
    new_df: DataFrame = DataFrame(data)

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


def get_data(driver: uc.Chrome, html: str, session: requests.Session) -> None:
    """
    Основная функция сбора данных с сайта: разработчики, проекты, цены.

    :param driver: WebDriver Chrome.
    :param html: HTML главной страницы с разработчиками.
    :param session: объект requests.Session.
    """
    batch_size: int = 100
    result_data: list[dict] = []
    prices_data: list[dict] = []

    soup = BeautifulSoup(html, 'lxml')
    developer_items = soup.find('div', class_='developments-table').find_all('div', class_='item')

    count_developers = len(developer_items)

    for i, developer_item  in enumerate(developer_items, 1):
        try:
            developer_data = developer_item.find_all('span')
        except Exception as ex:
            print(f'developer_data - {ex}')
            continue

        try:
            developer_name: str = developer_item.find('a').get_text(strip=True)
        except Exception:
            developer_name = ''
        if not developer_name:
            continue

        try:
            projects_count: str = developer_data[0].get_text(strip=True)
            if projects_count == '0':
                continue
        except Exception:
            projects_count = ''

        try:
            min_price: str = developer_data[1].get_text(strip=True)
        except Exception:
            min_price = ''

        try:
            max_price: str = developer_data[2].get_text(strip=True)
        except Exception:
            max_price = ''

        try:
            avg_price: str = developer_data[3].get_text(strip=True)
        except Exception:
            avg_price = ''

        try:
            developer_url: str = developer_item.find('a').get('href')
            html = scroll_and_get_html(driver, developer_url)
            soup = BeautifulSoup(html, 'lxml')
            project_items = soup.find('section', class_='developments-table single-developer-table').find_all('div', class_='item')
        except Exception as ex:
            print(f'url_developer - {ex}')
            continue

        for c in project_items:
            try:
                project_name: str = c.find('a').get_text(strip=True)
            except Exception:
                project_name = ''
            if not project_name:
                continue

            try:
                property_type: str = c.find('span', class_='text-capitalize').get_text(strip=True)
            except Exception:
                property_type = ''

            try:
                project_url: str = c.find('a').get('href')
                html = get_html(project_url, session)
                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(f'url_project - {ex}')
                continue

            # Сбор данных по проекту
            try:
                starting_price: str = soup.find('div', string=re.compile('Start price from')).find_next().get_text(strip=True)
            except Exception as ex:
                starting_price = ''
                exceptions_data.append({
                    'Developer URL': developer_url,
                    'Project URL': project_url,
                    'Error': str(ex)
                })

            try:
                price_per_sqft_from: str = soup.find('div', string=re.compile('Price Per Sqft from')).find_next().get_text(strip=True)
            except Exception:
                price_per_sqft_from = ''

            try:
                area_from: str = soup.find('div', string=re.compile('Area from')).find_next().get_text(strip=True)
            except Exception:
                area_from = ''

            try:
                type_: str = soup.find('div', string=re.compile('Type')).find_next().get_text(strip=True)
            except Exception:
                type_ = ''

            try:
                bedrooms: str = soup.find('div', string=re.compile('Bedrooms')).find_next().get_text(strip=True)
            except Exception:
                bedrooms = ''

            try:
                location: str = soup.find('div', string=re.compile('Location')).find_next().get_text(strip=True)
            except Exception:
                location = ''

            try:
                completion: str = soup.find('div', string=re.compile('Est. Completion')).find_next().get_text(strip=True)
            except Exception:
                completion = ''

            try:
                images_items = soup.find('div', class_='gallery-grid').find_all('div', class_='thickbox setThumbMe')
                images_urls: str = ', '.join(image_item.find('img').get('data-lazy-src') for image_item in images_items)
            except Exception:
                images_urls = ''

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
                    'Type': type_,
                    'Bedrooms': bedrooms,
                    'Location': location,
                    'Completion': completion,
                    'Developer link': developer_url,
                    'Project link': project_url,
                    'Images links': images_urls
                }
            )

            # Сохраняем партию данных result_data
            if len(result_data) >= batch_size:
                save_excel(result_data, 'result_data.xlsx')
                result_data.clear()

            try:
                price_range_items = soup.find('div', class_='prices-items').find_all('div', class_='item')
            except Exception:
                continue

            for item in price_range_items:
                try:
                    type_apartment: str = item.find('div', class_='first').get_text(strip=True)
                except Exception:
                    type_apartment = ''
                try:
                    size_apartment: str = item.find('div', class_='second').find_all('p')[1].get_text(strip=True)
                except Exception:
                    size_apartment = ''
                try:
                    price_apartment: str = item.find('div', class_='third').find_all('p')[1].get_text(strip=True)
                except Exception:
                    price_apartment = ''

                prices_data.append(
                    {
                        'Project link': project_url,
                        'Type': type_apartment,
                        'Size': size_apartment,
                        'Price': price_apartment
                    }
                )

                # Сохраняем партию данных prices_data
                if len(prices_data) >= batch_size:
                    save_excel(prices_data, 'prices_data.xlsx')
                    prices_data.clear()

            print(f'Developer: {developer_name}, Project: {project_name}')

        print(f'Обработано застройщиков: {i}/{count_developers}')

    # Сохраняем остатки
    if result_data:
        save_excel(result_data, 'result_data.xlsx')
    if prices_data:
        save_excel(prices_data, 'prices_data.xlsx')


def main() -> None:
    """
    Точка входа программы.
    """
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        html: str = scroll_and_get_html(driver, url="https://dxboffplan.com/list-of-property-developers-in-uae/")
        with requests.Session() as session:
            get_data(driver, html, session)
    finally:
        driver.close()
        driver.quit()

    # Сохраняем исключения
    if exceptions_data:
        save_excel(exceptions_data, 'exception_list.xlsx')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
