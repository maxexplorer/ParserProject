import os
import time
from datetime import datetime

from requests import Session
from pandas import DataFrame, ExcelWriter
from bs4 import BeautifulSoup

start_time = datetime.now()

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://gorod.mos.ru',
    'priority': 'u=1, i',
    'referer': 'https://gorod.mos.ru/news',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}


def get_html(url: str, headers: dict, session: Session) -> str:
    """
    Выполняет HTTP GET-запрос и возвращает HTML содержимое страницы.

    :param url: URL страницы
    :param headers: Заголовки запроса
    :param session: Сессия requests для повторного использования соединения
    :return: Строка с HTML содержимым страницы
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')
        return ""


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML.

    :param html: HTML код страницы
    :return: Количество страниц (если не найдено — возвращает 55 по умолчанию)
    """
    soup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу пагинации
        pages = int(soup.find('ul', class_='pagination').find_all('a')[-2].text.strip())
    except Exception:
        pages = 55  # Фолбэк, если структура изменится

    return pages


def get_json(headers: dict, session: Session, page: int) -> dict | None:
    """
    Получить JSON с новостями с указанной страницы.

    :param headers: Заголовки HTTP запроса
    :param session: Объект requests.Session для повторного использования соединения
    :param page: Номер страницы для запроса
    :return: JSON-ответ в виде словаря или None в случае ошибки
    """
    json_data = {
        'page': page,
        'search': '',
    }
    try:
        response = session.post('https://gorod.mos.ru/data/news/find', headers=headers, json=json_data, timeout=60)
        if response.status_code != 200:
            print(f'status_code: {response.status_code}')
            return None

        return response.json()
    except Exception as ex:
        print(f'get_json: {ex}')
        return None


def convert_timestamp_to_date(timestamp: int) -> str:
    """
    Преобразует UNIX timestamp в строку формата 'дд.мм.гггг'.

    :param timestamp: Целое число — UNIX-временная метка
    :return: Строка в формате 'дд.мм.гггг'
    """
    date = datetime.utcfromtimestamp(timestamp)
    return date.strftime('%d.%m.%Y')


def get_articles_data(headers: dict) -> list[dict[str, str | int | None]]:
    """
    Собирает данные статей с сайта, фильтруя по ключевому слову 'ТиНАО'.

    :param headers: Заголовки HTTP запроса
    :return: Список словарей с информацией по статьям
    """
    result_data = []

    with Session() as session:
        # Получаем HTML содержимое стартовой страницы новостей
        html = get_html(url="https://gorod.mos.ru/news", headers=headers, session=session)

        # Определяем количество страниц
        pages = get_pages(html=html)

        for page in range(pages + 1):
            try:
                time.sleep(1)  # Пауза между запросами, чтобы избежать блокировки
                # Получаем JSON данные для каждой страницы
                json_response = get_json(headers=headers, session=session, page=page)
            except Exception as ex:
                print(f"page: {page} - {ex}")
                continue

            if not json_response:
                continue

            data = json_response.get('data', {}).get('data_page')
            if not data:
                continue

            for item in data:
                title = item.get('title', '')
                text_preview = item.get('clearTextPreview', '')
                html_content = item.get('text', '')

                # Очищаем HTML из полного текста статьи
                soup = BeautifulSoup(html_content, "html.parser")
                text = soup.get_text(separator="\n").strip()

                timestamp = item.get('date_publish')
                if timestamp is None:
                    date = ''
                else:
                    date = convert_timestamp_to_date(timestamp=timestamp)

                count_view = item.get('count_view')

                # Фильтрация по ключевому слову 'ТиНАО'
                if not any('ТиНАО' in field for field in (title, text_preview, text) if field):
                    continue

                result_data.append(
                    {
                        'Заголовок': title,
                        'Краткое содержание': text_preview,
                        'Дата публикации': date,
                        'Количество просмотров': count_view,
                    }
                )

            print(f'Обработано страниц : {page}')

    return result_data


def save_excel(data: list[dict[str, str | int | None]]) -> None:
    """
    Сохраняет список словарей с данными в Excel файл.

    :param data: Список словарей с данными
    """
    directory = 'results'
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, 'result_data.xlsx')

    dataframe = DataFrame(data)
    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main() -> None:
    """
    Основная функция запуска скрипта.
    Собирает данные и сохраняет их в Excel.
    """
    try:
        result_data = get_articles_data(headers=headers)
        save_excel(data=result_data)
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
