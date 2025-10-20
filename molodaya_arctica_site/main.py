import os
import time
from datetime import datetime

from requests import Session

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

start_time: datetime = datetime.now()


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
    driver.implicitly_wait(1)
    driver.maximize_window()
    return driver


def get_product_ids(file_path: str) -> None:
    with Session() as session:
        vacancy_ids = []

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://molodaya-arctica.ru/jobs',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'X-XSRF-TOKEN': 'eyJpdiI6ImxaSEFYOGI5bGJraGl2M1BqQjRwNkE9PSIsInZhbHVlIjoiVDlIV2MvQjh6cDNRUXlya0hSc1RBcVlZOGpYaFZIZjNzT3FKcXRaeFViekVWTlhHbWNsWFVSNTlYV3lXODMyQzhvazlTYmJZMWtNb3gwaytaMWV6aXdxNnZ1V0o5SGhBV1U1ZFB6cCtJczhKQjZ0WjE4Y3RBY3YxSjBuSUt6TW4iLCJtYWMiOiJhMzg5MjllOWZhNzRiMGE1NGE0M2UxYjlmNzBjMmEwY2M1ODFiNjE1YjcxYzQzNDgxMjk2ZjI5ODc4MjdiNGYyIiwidGFnIjoiIn0=',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        first_params = {
            'page': 1,

        }

        response = session.get(
            'https://molodaya-arctica.ru/api/vacancies',
            headers=headers,
            params=first_params,
            timeout=(3, 5)
        )

        response.raise_for_status()
        json_data = response.json()

        total = json_data.get('total', 0)

        pages = json_data.get('last_page', 1)

        print(f"Всего {total} вакансий, {pages} страниц")

        # Цикл по страницам
        for page in range(1, pages + 1):
            params = first_params.copy()
            params['pages'] = page

            try:
                time.sleep(1)
                response = session.get(
                    'https://molodaya-arctica.ru/api/vacancies',
                    headers=headers,
                    params=first_params,
                    timeout=(3, 5)
                )

                if response.status_code != 200:
                    print(f'Страница: {page}: статус ответа {response.status_code}')
                    continue

                json_data: dict = response.json()
                items: list = json_data.get('resources', [])

            except Exception as ex:
                print(f"Страница {page}: {ex}")
                continue

            if not items:
                continue

            # Обработка товаров на странице
            for item in items:
                vacancy_id = item.get('id')

                vacancy_ids.append(vacancy_id)

            print(f"Обработано страниц: {page}/{pages}")

    with open(file_path, 'w', encoding='utf-8') as file:
        print(*vacancy_ids, file=file, sep='\n')


def process_vacancy_ids(driver, file_path: str) -> None:
    """
    Обрабатывает список вакансий:
    - Нажимает "Откликнуться"
    - Переключается на новую вкладку
    - Проверяет скрытые вакансии
    - Сохраняет результаты в файл
    """

    directory: str = 'results'
    os.makedirs(directory, exist_ok=True)
    result_file = os.path.join(directory, 'result_data.txt')

    total_processed = 0
    hidden_count = 0

    # Загружаем данные
    with open(file_path, 'r', encoding='utf-8') as file:
        vacancy_ids = [line.strip() for line in file.readlines()]

    total_count = len(vacancy_ids)

    for i, vacancy_id in enumerate(vacancy_ids, start=1):
        total_processed += 1
        print(f"🔄 Обработка {i}/{total_count}: Вакансия {vacancy_id}")

        try:
            # Открываем вакансию
            driver.get(url=f"https://molodaya-arctica.ru/jobs/{vacancy_id}")

            html = driver.page_source

            # Кликаем по кнопке "Откликнуться"
            # Ждём, пока ссылка с текстом "Откликнуться" станет кликабельной
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/div/div/a/span")
                )
            )

            # Кликаем через JavaScript, чтобы обойти overlay или hidden state
            button.click()

            # Ждём открытия новой вкладки
            WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])

            # Ждём полной загрузки страницы
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Проверяем заголовок
            try:
                title_el = driver.find_element(By.XPATH, "//h1[@class='content__title']")
                if "Вакансия была скрыта или удалена работодателем" in title_el.text:
                    hidden_count += 1
                    with open(result_file, 'a', encoding='utf-8') as f:
                        f.write(f"{vacancy_id}\n")
                    print(f"✅ Вакансия {vacancy_id} скрыта — ID сохранён.")
            except NoSuchElementException:
                pass

        except Exception as ex:
            continue

        finally:
            # Закрываем новую вкладку (если она есть) и возвращаемся
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    # В конце добавляем статистику
    with open(result_file, 'a', encoding='utf-8') as f:
        f.write(f"\nВсего обработано: {total_processed}\n")
        f.write(f"Скрытых вакансий: {hidden_count}\n")

    print(f"📊 Обработка завершена: всего {total_processed}, скрытых {hidden_count}")


def main() -> None:
    directory: str = 'data'
    os.makedirs(directory, exist_ok=True)

    file_name = 'vacancy_ids.txt'

    file_path = os.path.join(directory, file_name)

    # get_product_ids(file_path=file_path)

    driver = init_undetected_chromedriver(headless_mode=True)
    try:
        process_vacancy_ids(driver=driver, file_path=file_path)
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
