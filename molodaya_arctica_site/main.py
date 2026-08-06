import os
import time
from datetime import datetime
from html.parser import HTMLParser

from requests import Session
from requests.exceptions import RequestException

# Начало отсчёта времени выполнения
start_time: datetime = datetime.now()

BASE_URL = 'https://molodaya-arctica.ru'
VACANCIES_API_URL = f'{BASE_URL}/api/vacancies'
REQUEST_TIMEOUT = (5, 20)
MAX_RETRIES = 3
REQUEST_DELAY = 0.3

HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': f'{BASE_URL}/jobs',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


class ApplyLinkParser(HTMLParser):
    """
    Простой HTML-парсер для сбора ссылок со страницы вакансии.

    Нужен, чтобы достать href кнопки "Откликнуться" без Selenium.
    В self.links сохраняются кортежи вида: (href, text).
    """

    def __init__(self):
        super().__init__()
        self.links = []
        self._current_link = None

    def handle_starttag(self, tag, attrs):
        """Запоминает начало ссылки <a> и её href."""
        if tag == 'a':
            self._current_link = {
                'href': dict(attrs).get('href'),
                'text': [],
            }

    def handle_data(self, data):
        """Собирает текст внутри текущей ссылки."""
        if self._current_link is not None:
            self._current_link['text'].append(data)

    def handle_endtag(self, tag):
        """На закрытии </a> сохраняет ссылку и её очищенный текст."""
        if tag == 'a' and self._current_link is not None:
            self.links.append((
                self._current_link['href'],
                ' '.join(''.join(self._current_link['text']).split()),
            ))
            self._current_link = None


def request_with_retries(session: Session, url: str, **kwargs):
    """
    Выполняет GET-запрос с небольшой паузой, таймаутом и повторами.

    Ошибки сети и ответы 5xx повторяются до MAX_RETRIES раз.
    Ответы 4xx возвращаются сразу: например 404 на trudvsem.ru означает,
    что вакансия скрыта или удалена.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Небольшая пауза есть даже перед первой попыткой.
            time.sleep(REQUEST_DELAY)
            response = session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
            if response.status_code < 500:
                return response
            last_error = f'status {response.status_code}'
        except RequestException as ex:
            last_error = ex

        if attempt < MAX_RETRIES:
            time.sleep(attempt)

    raise RuntimeError(f'{url}: {last_error}')


def load_ids(file_path: str) -> set[str]:
    """
    Загружает числовые ID из файла в set.

    Если файла ещё нет, возвращает пустой set, чтобы первый запуск начинался
    без ошибок.
    """
    if not os.path.exists(file_path):
        return set()

    with open(file_path, 'r', encoding='utf-8') as file:
        return {
            line.strip()
            for line in file
            if line.strip().isdigit()
        }


def append_id(file_path: str, vacancy_id: str) -> None:
    """Добавляет один ID в конец файла."""
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f'{vacancy_id}\n')


def get_apply_url(session: Session, vacancy_id: str) -> str:
    """
    Получает ссылку "Откликнуться" для вакансии на molodaya-arctica.ru.

    На странице вакансии эта кнопка ведёт на trudvsem.ru. Мы достаём её href
    из HTML напрямую, без открытия браузера и клика Selenium.
    """
    response = request_with_retries(
        session,
        f'{BASE_URL}/jobs/{vacancy_id}',
        headers=HEADERS,
    )

    response.raise_for_status()

    parser = ApplyLinkParser()
    parser.feed(response.text)

    # На странице есть две одинаковые кнопки "Откликнуться"; достаточно первой.
    for href, _ in parser.links:
        if href and 'trudvsem.ru/vacancy/card' in href:
            return href

    raise ValueError('ссылка "Откликнуться" не найдена')


def is_hidden_vacancy(session: Session, apply_url: str) -> bool:
    """
    Проверяет, скрыта ли вакансия на trudvsem.ru.

    Для скрытых/удалённых вакансий trudvsem.ru часто отдаёт 404/410.
    Дополнительно проверяем текст страницы на случай, если сайт вернул 200
    со страницей-заглушкой.
    """
    response = request_with_retries(
        session,
        apply_url,
        headers=HEADERS,
        allow_redirects=True,
    )

    if response.status_code in {404, 410}:
        return True

    response.raise_for_status()
    page_text = response.text

    return (
        'Вакансия была скрыта' in page_text
        or 'скрыта или удалена работодателем' in page_text
    )


def get_product_ids(file_path: str) -> None:
    """
    Получает все ID вакансий через API и сохраняет их в текстовый файл.

    :param file_path: Путь к файлу для сохранения ID вакансий.
    """
    with Session() as session:
        vacancy_ids = []

        first_params = {
            'page': 1,
        }

        # Получаем первую страницу, чтобы узнать общее количество
        response = request_with_retries(
            session,
            VACANCIES_API_URL,
            headers=HEADERS,
            params=first_params,
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
                response = request_with_retries(
                    session,
                    VACANCIES_API_URL,
                    headers=HEADERS,
                    params=params,
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


def process_vacancy_ids(file_path: str) -> None:
    """
    Обрабатывает вакансии:
    1. Открывает страницу вакансии прямым HTTP-запросом
    2. Достаёт ссылку "Откликнуться" на trudvsem.ru
    3. Проверяет, скрыта ли вакансия
    4. Сохраняет ID скрытых вакансий в result_data.txt
    5. Сохраняет прогресс в processed_ids.txt

    :param file_path: путь к файлу с ID вакансий
    """

    directory: str = 'results'
    os.makedirs(directory, exist_ok=True)
    result_file = os.path.join(directory, 'result_data.txt')
    processed_file = os.path.join(directory, 'processed_ids.txt')
    exceptions_file = os.path.join(directory, 'exceptions_list.txt')

    total_processed = 0
    # result_data.txt хранит найденные скрытые вакансии, processed_ids.txt — все успешно проверенные.
    hidden_ids = load_ids(result_file)
    processed_ids = load_ids(processed_file)
    exceptions_list = []

    # Загружаем список вакансий
    with open(file_path, 'r', encoding='utf-8') as file:
        # dict.fromkeys убирает дубли и сохраняет исходный порядок ID.
        vacancy_ids = list(dict.fromkeys(
            line.strip()
            for line in file.readlines()
            if line.strip()
        ))

        total_count = len(vacancy_ids)

    with Session() as session:
        for i, vacancy_id in enumerate(vacancy_ids, start=1):
            # processed_ids позволяет продолжить работу после остановки скрипта.
            if vacancy_id in processed_ids:
                continue

            print(f"🔄 Обработка {i}/{total_count}: Вакансия {vacancy_id}")

            try:
                apply_url = get_apply_url(session=session, vacancy_id=vacancy_id)

                if is_hidden_vacancy(session=session, apply_url=apply_url):
                    # hidden_ids защищает result_data.txt от дублей при повторном запуске.
                    if vacancy_id not in hidden_ids:
                        hidden_ids.add(vacancy_id)
                        append_id(result_file, vacancy_id)
                    print(f'✅ Вакансия {vacancy_id} скрыта — ID сохранён.')

                append_id(processed_file, vacancy_id)
                processed_ids.add(vacancy_id)
                total_processed += 1
            except Exception as ex:
                exceptions_list.append(vacancy_id)
                print(f'⚠️ Вакансия {vacancy_id}: {ex}')

    # В конце добавляем статистику
    with open(result_file, 'a', encoding='utf-8') as f:
        f.write(f'\nВсего обработано: {total_processed}\n')
        f.write(f'Скрытых вакансий: {len(hidden_ids)}\n')

    with open(exceptions_file, 'w', encoding='utf-8') as file:
        print(*exceptions_list, file=file, sep='\n')

    print(f"📊 Обработка завершена: всего {total_processed}, скрытых {len(hidden_ids)}")


def main() -> None:
    """
    Основная функция:
    1. Создаёт папку data
    2. Получает список вакансий
    3. Проверяет вакансии прямыми HTTP-запросами
    4. Выводит время выполнения
    """
    directory: str = 'data'
    os.makedirs(directory, exist_ok=True)

    file_name = 'vacancy_ids.txt'
    file_path = os.path.join(directory, file_name)

    # Получение вакансий (можно раскомментировать)
    get_product_ids(file_path=file_path)

    process_vacancy_ids(file_path=file_path)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
