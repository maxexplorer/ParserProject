import os
import time
from datetime import datetime
import re

from requests import Session

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options as ChromeOptions

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

# Отметка начала выполнения
start_time: datetime = datetime.now()

headers = {
    'Referer': 'https://connect.mysportel.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def init_undetected_chromedriver(headless_mode: bool = False):
    """
    Инициализирует браузер Chrome с использованием undetected_chromedriver.

    Args:
        headless_mode (bool): Если True — запускается без GUI.

    Returns:
        WebDriver: Экземпляр драйвера Chrome.
    """
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver = uc.Chrome(version_main=156, options=options)
    driver.implicitly_wait(1)
    driver.maximize_window()
    return driver


def save_excel(data: list[dict], sheet_name: str) -> None:
    """
    Сохраняет данные в Excel-файл. Если файла нет — создаёт.
    Если есть — дописывает новые строки в конец.

    Args:
        data (list[dict]): Список словарей с извлечёнными данными.
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    # Создаём директорию при необходимости
    os.makedirs(directory, exist_ok=True)

    # Создать пустой Excel-файл, если он отсутствует
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    # Загружаем существующие данные
    df_existing = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows = len(df_existing.index)

    # Добавляем новые строки
    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows + 1,
            header=(num_existing_rows == 0),
            sheet_name=sheet_name,
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def process_participants_ids(driver) -> None:
    """
    Обрабатывает участников по ID, собирает с каждой страницы:
    - имя
    - должность
    - компанию
    - профиль
    - email
    - телефон

    Работает пакетами по 100 записей для уменьшения нагрузки.

    Args:
        driver (WebDriver): Активный экземпляр браузера.
    """
    batch_size = 100
    result_data: list[dict] = []

    for participant_id in range(1, 3265):

        print(f"📊 Обработка: {participant_id}/3264")

        try:
            time.sleep(1)
            driver.get(f"https://connect.mysportel.com/details/participant/{participant_id}")
        except Exception:
            continue

        html = driver.page_source
        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')

        # Имя
        try:
            name = soup.find('h2', class_='g-font-weight-300 g-mr-10').get_text(strip=True)
        except Exception:
            name = ''

        if not name:
            continue

        # Блоки с должностью, компанией и другими данными
        items = soup.find_all('h4', class_='h6 g-font-weight-300 g-mb-10')
        if not items:
            continue

        # Должность и компания — всегда первые два h4
        position = items[0].get_text(strip=True) if len(items) > 0 else ''
        company = items[1].get_text(strip=True) if len(items) > 1 else ''

        # Профиль, email, телефон — через <b>
        try:
            profile = soup.find('b', string=re.compile('Profile:')).next_sibling.strip()
        except Exception:
            profile = ''

        try:
            email = soup.find('b', string=re.compile('Email address:')).next_sibling.strip()
        except Exception:
            email = ''

        try:
            phone = soup.find('b', string=re.compile('Phone:')).next_sibling.strip()
        except Exception:
            phone = ''

        result_data.append({
            'name': name,
            'position': position,
            'company': company,
            'profile': profile,
            'email': email,
            'phone': phone,
        })

        # Сохраняем пакетами по 100
        if len(result_data) >= batch_size:
            save_excel(result_data, sheet_name='Participants')
            result_data.clear()

    # Сохранение последних данных
    if result_data:
        save_excel(result_data, sheet_name='Participants')


def process_companies_ids(driver) -> None:
    """
    Обрабатывает участников по ID, собирает с каждой страницы:
    - имя
    - должность
    - компанию
    - профиль
    - email
    - телефон

    Работает пакетами по 100 записей для уменьшения нагрузки.

    Args:
        driver (WebDriver): Активный экземпляр браузера.
    """
    batch_size = 100
    result_data: list[dict] = []

    for company_id in range(1, 2073):

        print(f"📊 Обработка: {company_id}/3264")

        try:
            time.sleep(1)
            driver.get(f"https://connect.mysportel.com/details/company/{company_id}")
        except Exception:
            continue

        html = driver.page_source
        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')

        # Имя
        try:
            company = soup.find('span', class_='d-block g-font-size-18 g-color-gray-dark-v1').get_text(strip=True)
        except Exception:
            company = ''

        if not company:
            continue

        try:
            country = soup.find('b', string=re.compile('Country:')).next_sibling.strip()
        except Exception:
            country = ''

        try:
            participants = ', '.join(
                a.get_text(strip=True)
                for a in soup.select('tbody.text-center td.js-details-show a')
            )
        except Exception:
            participants = ''

        if not participants:
            continue

        result_data.append({
            'company': company,
            'country': country,
            'participants': participants,
        })

        # Сохраняем пакетами по 100
        if len(result_data) >= batch_size:
            save_excel(result_data, sheet_name='Companies')
            result_data.clear()

    # Сохранение последних данных
    if result_data:
        save_excel(result_data, sheet_name='Companies')


def download_imgs(session: Session, image_url: str, name: str) -> None:
    directory = 'images'

    # Создаём директорию при необходимости
    os.makedirs(directory, exist_ok=True)

    response = session.get(url=image_url, headers=headers)

    with open(f"images/{name}.jpg", "wb") as file:
        file.write(response.content)

    print(f'Обработано фото: {name}')


def process_participants_photo(driver) -> None:
    """
    Обрабатывает участников по ID, собирает с каждой страницы:
    - имя
    - должность
    - компанию
    - профиль
    - email
    - телефон

    Работает пакетами по 100 записей для уменьшения нагрузки.

    Args:
        driver (WebDriver): Активный экземпляр браузера.
    """

    with Session() as session:
        for participant_id in range(1, 3265):

            print(f"📊 Обработка: {participant_id}/3264")

            try:
                time.sleep(1)
                driver.get(f"https://connect.mysportel.com/details/participant/{participant_id}")
            except Exception:
                continue

            html = driver.page_source
            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            # Имя
            try:
                name = soup.find('h2', class_='g-font-weight-300 g-mr-10').get_text(strip=True)
            except Exception:
                name = ''

            if not name:
                continue

            try:
                image_url = f"https://connect.mysportel.com{soup.find('div', class_='g-mb-20').find('img').get('src')}"
            except Exception:
                image_url = ''

            if 'anonymous' in image_url:
                continue

            download_imgs(session, image_url, name)


def main() -> None:
    """
    Основная функция:
    1. Запускает Chrome через undetected_chromedriver.
    2. Открывает страницу логина.
    3. Ждёт ручной авторизации пользователя.
    4. Запускает процесс сбора данных.
    5. Закрывает браузер.
    """
    driver = init_undetected_chromedriver(headless_mode=False)

    try:
        driver.get("https://connect.mysportel.com/login")
        print("⏳ У вас есть 30 секунд, чтобы авторизоваться вручную...")
        time.sleep(30)

        process_participants_ids(driver=driver)
        process_companies_ids(driver=driver)
        process_participants_photo(driver=driver)
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершён.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
