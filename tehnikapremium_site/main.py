import os
import time
from datetime import datetime
import json

from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

# Засекаем время работы программы
start_time = datetime.now()

# Заголовки для HTTP-запросов
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=0, i',
    'referer': 'https://tehnikapremium.ru/catalog/vstraivaemye_rabochie_poverkhnosti/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}


def get_html(url: str, headers: dict, session: Session) -> str | None:
    """
    Загружает HTML-код страницы по переданному URL.

    :param url: адрес страницы для загрузки
    :param headers: словарь с HTTP-заголовками
    :param session: объект requests.Session для повторного использования соединений
    :return: HTML-код страницы (str) или None при ошибке
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f'status_code: {response.status_code}')
        return response.text
    except Exception as ex:
        print(f'get_html: {ex}')
        return None


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML-кода.

    Аргументы:
        html: HTML-код страницы категории.

    Возвращает:
        Целое число — количество страниц пагинации.
        Если пагинация не найдена, возвращает 1.
    """
    soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу в блоке пагинации
        pages: int = int(soup.find('div', class_='module-pagination').find_all('a')[-2].get_text(strip=True))
        return pages
    except Exception:
        # Если пагинации нет — возвращаем 1
        return 1


def get_category_urls(url: str, headers: dict) -> None:
    category_data = []

    with Session() as session:
        try:
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f'get_category_urls: {ex}')

        if not html:
            raise 'not html'

        soup = BeautifulSoup(html, 'lxml')

        try:
            category_items = soup.find('div', class_='catalog_section_list row items flexbox').find_all('td',
                                                                                                        class_='section_info')
        except Exception as ex:
            print(f'category_items: {ex}')

        for category_item in category_items:
            try:
                category_name = category_item.find('li', class_='name').get_text(strip=True)
            except Exception as ex:
                print(f'category_name: {ex}')
                continue

            try:
                category_url = f"https://tehnikapremium.ru{category_item.find('a').get('href')}"
            except Exception as ex:
                print(f'category_url: {ex}')
                continue

            category_data.append({category_name: category_url})

    # Сохраняем список ссылок в JSON
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/category_data.json', 'w', encoding='utf-8') as file:
        json.dump(category_data, file, indent=4, ensure_ascii=False)


def get_products_data(file_path: str, headers: dict) -> list:
    """
    Загружает данные о товарах с API сайта и сохраняет их партиями в Excel.

    :param file_path: путь к файлу с URL товаров
    :param headers: словарь с HTTP-заголовками
    :return: список словарей с данными о товарах
    """
    # Читаем product_data_list из JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        category_data: list = json.load(file)

    batch_size = 1000
    result_data = []

    with Session() as session:
        for category_dict in category_data[24:]:
            category_name, category_url = next(iter(category_dict.items()))

            print(f'Обработка категории: {category_name}')

            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_data: {ex}')

            if not html:
                continue

            # Определяем количество страниц
            pages: int = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url: str = f"{category_url}?PAGEN_2={page}"

                try:
                    time.sleep(1)  # Задержка, чтобы не перегружать сайт
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup: BeautifulSoup = BeautifulSoup(html, 'lxml')

                try:
                    product_items = soup.find_all('div',
                                                  class_='item_block col-4 col-md-3 col-sm-6 col-xs-6 js-notice-block')
                except Exception as ex:
                    print(f'product_items: {ex}')
                    continue

                for product_item in product_items:
                    try:
                        product_name = product_item.find('div', class_='item-title').find('span').get_text(strip=True)
                    except Exception:
                        product_name = ''

                    try:
                        model = product_item.find('img', class_='img-responsive').get('title')
                    except Exception:
                        model = ''

                    brands_with_two_words = ['De Dietrich', 'Jet Air']
                    model_lower = model.lower()

                    if any(b.lower() in model_lower for b in brands_with_two_words):
                        brand = ' '.join(model.split()[:2])
                    else:
                        brand = model.split()[0]

                    # Удаляем бренд из строки model
                    model_clean = model.replace(brand, '').strip()

                    # Удаляем model из строки product_name
                    product_name_clean = product_name.replace(model, '').strip()

                    if len(product_name_clean) == 0:
                        product_name_clean = category_name

                    try:
                        price = product_item.find('span', class_='price_value').get_text(strip=True)
                    except Exception:
                        price = ''

                    result_data.append({
                        'Товар': product_name_clean,
                        'Бренд': brand,
                        'Модель': model_clean,
                        'Цена': price,

                    })

                    if len(result_data) >= batch_size:
                        save_excel(result_data)
                        result_data.clear()

                print(f'Обработано страниц: {page}/{pages}')

    if result_data:
        save_excel(result_data)

    return result_data


def save_excel(data: list) -> None:
    """
    Сохраняет список товаров в Excel (results/result_data.xlsx).

    :param data: список словарей с данными о товарах
    """
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)

    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1,
                        header=(num_existing_rows == 0),
                        sheet_name='Data', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def main():
    """
    Основная функция программы.
    Собирает данные о товарах и сохраняет их в Excel.
    """

    # get_category_urls(url="https://tehnikapremium.ru/catalog/", headers=headers)
    get_products_data(file_path='data/category_data.json', headers=headers)

    execution_time = datetime.now() - start_time
    print('✅ Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
