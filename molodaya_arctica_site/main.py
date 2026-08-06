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

# Начало отсчёта времени выполнения
start_time: datetime = datetime.now()


def init_undetected_chromedriver(headless_mode: bool = False):
    """
    Инициализирует браузер Chrome с использованием undetected_chromedriver.

    :param headless_mode: Если True — браузер запускается без интерфейса.
    :return: объект WebDriver для управления браузером.
    """
    options = ChromeOptions()
    if headless_mode:
        options.add_argument('--headless')

    driver = uc.Chrome(options=options, version_main=151)
    driver.implicitly_wait(1)  # неявное ожидание для всех элементов
    driver.maximize_window()  # максимальный размер окна для корректной работы элементов
    return driver


def get_product_ids(file_path: str) -> None:
    """
    Получает все ID вакансий через API и сохраняет их в текстовый файл.

    :param file_path: Путь к файлу для сохранения ID вакансий.
    """
    with Session() as session:
        vacancy_ids = []

        # Заголовки запроса
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

        # Получаем первую страницу, чтобы узнать общее количество
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
            params['page'] = page

            try:
                time.sleep(1)  # пауза между запросами
                response = session.get(
                    'https://molodaya-arctica.ru/api/vacancies',
                    headers=headers,
                    params=params,
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

            # Сохраняем ID вакансий
            for item in items:
                vacancy_id = item.get('id')
                vacancy_ids.append(vacancy_id)

            print(f"Обработано страниц: {page}/{pages}")

    # Сохраняем все ID в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        print(*vacancy_ids, file=file, sep='\n')


def process_vacancy_ids(driver, file_path: str) -> None:
    """
    Обрабатывает вакансии:
    1. Открывает страницу вакансии
    2. Кликает кнопку "Откликнуться"
    3. Переключается на новую вкладку
    4. Проверяет, скрыта ли вакансия
    5. Сохраняет ID скрытых вакансий в result_data.txt
    6. Выводит прогресс i/total и статистику по скрытым вакансиям

    :param driver: объект WebDriver
    :param file_path: путь к файлу с ID вакансий
    """

    exceptions_list = []

    directory: str = 'results'
    os.makedirs(directory, exist_ok=True)
    result_file = os.path.join(directory, 'result_data.txt')

    total_processed = 0
    hidden_count = 0

    # Загружаем список вакансий
    with open(file_path, 'r', encoding='utf-8') as file:
        vacancy_ids = [line.strip() for line in file.readlines()]

    total_count = len(vacancy_ids)

    for i, vacancy_id in enumerate(vacancy_ids, start=1):
        total_processed += 1
        print(f"🔄 Обработка {i}/{total_count}: Вакансия {vacancy_id}")

        try:
            # Открываем страницу вакансии
            driver.get(url=f"https://molodaya-arctica.ru/jobs/{vacancy_id}")

            # Ждём кнопку "Откликнуться" и кликаем по ней
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div/div/main/div/div[2]/div/div/div/a/span')
                )
            )
            button.click()

            # Ждём открытия новой вкладки и переключаемся
            WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[-1])

            # Ждём полной загрузки новой страницы
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # Проверяем, скрыта ли вакансия
            try:
                title_el = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[@class='content__title']"))
                )
                if 'Вакансия была скрыта или удалена работодателем' in title_el.text:
                    hidden_count += 1
                    with open(result_file, 'a', encoding='utf-8') as f:
                        f.write(f"{vacancy_id}\n")
                    print(f'✅ Вакансия {vacancy_id} скрыта — ID сохранён.')
            except NoSuchElementException:
                pass

        except Exception:
            # Игнорируем ошибки, чтобы не прерывать цикл
            exceptions_list.append(vacancy_id)
            continue

        finally:
            # Закрываем вкладку с формой и возвращаемся на основную
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    # В конце добавляем статистику
    with open(result_file, 'a', encoding='utf-8') as f:
        f.write(f'\nВсего обработано: {total_processed}\n')
        f.write(f'Скрытых вакансий: {hidden_count}\n')

    with open('data/exceptions_list.txt', 'w', encoding='utf-8') as file:
        print(*exceptions_list, file=file, sep='\n')

    print(f"📊 Обработка завершена: всего {total_processed}, скрытых {hidden_count}")


def main() -> None:
    """
    Основная функция:
    1. Создаёт папку data
    2. Получает список вакансий (закомментировано для теста)
    3. Запускает Chrome через undetected_chromedriver
    4. Запускает обработку вакансий
    5. Закрывает браузер и выводит время выполнения
    """
    directory: str = 'data'
    os.makedirs(directory, exist_ok=True)

    file_name = 'vacancy_ids.txt'
    file_path = os.path.join(directory, file_name)

    # Получение вакансий (можно раскомментировать)
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
