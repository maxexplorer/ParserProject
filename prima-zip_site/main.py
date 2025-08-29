import os
import time
from datetime import datetime
import json
import re

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}

category_dict = {
    'Насосы и запчасти': 'https://prima-zip.ru/catalog/Nasosy-i-zapchasti',
    'Насосы и запчасти/Торцовые уплотнения для насосов': 'https://prima-zip.ru/catalog/Torcovye-uplotneniya',
    'Насосы и запчасти/Запасные части к установке СИН': 'https://prima-zip.ru/catalog/Zapasnye-chasti-k-ustanovke-SIN',
    'Насосы и запчасти/Буровое оборудование и ЗиП': 'https://prima-zip.ru/catalog/Burovye-nasosy-i-zapchasti-k-nim',
    'Запчасти к спецтехнике': 'https://prima-zip.ru/catalog/Zapchasti-k-PPUA1600',
    'Запчасти к спецтехнике/КиП и оборудование': 'https://prima-zip.ru/catalog/KIP-i-pribory-dlya-PPUA-i-ADPM',
    'Запчасти к спецтехнике/Запчасти к ППУА1600/АДПМ': 'https://prima-zip.ru/catalog/Zapchasti-k-PPUA1600-3',
    'Запорная арматура': 'https://prima-zip.ru/catalog/Zapornaya-armatura-2',
    'Запорная арматура/Краны шаровые': 'https://prima-zip.ru/catalog/KRANY-ShAROVYe',
    'Запорная арматура/Задвижки': 'https://prima-zip.ru/catalog/ZADVIZhKI',
    'Запорная арматура/Клапаны запорные': 'https://prima-zip.ru/catalog/KLAPANY-ZAPORNYe',
    'Запорная арматура/Клапаны обратные': 'https://prima-zip.ru/catalog/KLAPANY-OBRATNYe',
}


def get_html(url: str, headers: dict, session: Session) -> str | None:
    """
    Выполняет GET-запрос по указанному URL и возвращает HTML-код страницы.

    :param url: Ссылка на страницу
    :param headers: Заголовки запроса (user-agent и др.)
    :param session: Сессия requests для повторного использования соединений
    :return: HTML содержимое страницы или None в случае ошибки
    """
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')
        return None


def get_pages(html: str) -> int:
    """
    Определяет количество страниц пагинации на основе HTML.

    :param html: HTML код страницы
    :return: Количество страниц (если не найдено — возвращает 55 по умолчанию)
    """
    soup = BeautifulSoup(html, 'lxml')

    try:
        # Ищем последнюю страницу пагинации
        page_url = soup.find('div', class_='pages').find('li', class_='last').find('a').get('href')
        match = re.search(r"page=(\d+)", page_url)
        return int(match.group(1)) if match else 1
    except Exception:
        return 1


def get_products_urls(category_dict: dict, headers: dict) -> list[dict]:
    """
    Собирает ссылки на товары по категориям.

    :param category_dict: Словарь со ссылками на страницы каталога
    :param headers: Заголовки запроса
    :return: Список словарей {имя_категории: [список ссылок на товары]}
    """

    product_data_list = []

    # Создаем requests.Session для ускорения запросов
    with Session() as session:
        for category_name, category_url in category_dict.items():
            product_urls = []
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f'get_products_urls: {category_url} - {ex}')
                continue

            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url = f"{category_url}?&page={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                # Получаем список категорий
                try:
                    product_items = soup.find('div', class_='products-grid row').find_all('div', class_='product-name')
                except Exception as ex:
                    print(f'data: {ex}')
                    product_items = []

                # Перебираем категории
                for product_item in product_items:
                    try:
                        product_url = product_item.find('a', itemprop='url').get('href')
                    except Exception:
                        product_url = None
                    product_urls.append(product_url)

                print(f'ОБработано страниц: {page}/{pages}')

            product_data_list.append({category_name: product_urls})

            print(f'Обработано категория: {category_name}')

    # Сохраняем список ссылок в JSON
    directory = 'data'
    os.makedirs(directory, exist_ok=True)

    with open('data/product_data_list.json', 'w', encoding='utf-8') as file:
        json.dump(product_data_list, file, indent=4, ensure_ascii=False)

    return product_data_list


def get_products_data(file_path: str) -> None:
    """
    Извлекает данные о товарах (название, описание, характеристики, фото и т.д.)
    по ссылкам из сохранённого JSON-файла.

    :param file_path: Путь к JSON-файлу с категориями и ссылками на товары
    :return: Список словарей с данными о каждом товаре
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        product_data_list = json.load(file)



    # Создаем requests.Session для ускорения
    with Session() as session:
        for category_dict in product_data_list:
            for category_name, product_urls in category_dict.items():
                result_data = []
                image_url_list = []
                for product_url in product_urls:
                    try:
                        time.sleep(1)  # пауза между запросами
                        html = get_html(url=product_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{product_url} - {ex}")
                        continue

                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'lxml')

                    # Название товара
                    try:
                        title = soup.find('h1', itemprop='name').text.strip()
                    except Exception:
                        title = ''

                    # Изображения
                    try:
                        image_url = soup.find('div', class_='general-img').find('a').get('href')
                        image_url_list.append(image_url)
                    except Exception:
                        image_url = None

                    # Блок с описанием
                    try:
                        content_data = soup.find('div', id='content_1')
                    except Exception as ex:
                        print(f'content_data: {product_url} - {ex}')
                        continue

                    # Текстовое описание
                    try:
                        description = ' '.join(i.text.strip().replace('\xa0', ' ') for i in content_data.find_all('p'))
                    except Exception:
                        description = ''

                    # Характеристики (таблица)
                    try:
                        characteristic = ''
                        characteristic_items = content_data.find('table').find_all('tr')
                        for characteristic_item in characteristic_items:
                            characteristic += '\n' + ' '.join(
                                c.text.strip().replace('\xa0', ' ') for c in characteristic_item.find_all('td'))
                    except Exception:
                        characteristic = ''

                    description = f'{description}\n{characteristic}'

                    # Добавляем словарь с данными товара
                    result_data.append(
                        {
                            'Код_товара': None,
                            'Название_позиции': title,
                            'Поисковые_запросы': f'{title}, {category_name}',
                            'Описание': description,
                            'Тип_товара': 'u',
                            'Цена': None,
                            'Цена от': None,
                            'Ярлык': None,
                            'HTML_заголовок': None,
                            'HTML_описание': None,
                            'HTML_ключевые_слова': None,
                            'Валюта': '',
                            'Скидка': '',
                            'Cрок действия скидки от': None,
                            'Cрок действия скидки до': None,
                            'Единица_измерения': 1,
                            'Минимальный_объем_заказа': None,
                            'Оптовая_цена': None,
                            'Минимальный_заказ_опт': None,
                            'Ссылка_изображения': image_url,
                            'Наличие': '+',
                            'Количество': None,
                            'Производитель': None,
                            'Страна_производитель': None,
                            'Номер_группы': None,
                            'Адрес_подраздела': None,
                            'Возможность_поставки': None,
                            'Срок_поставки': None,
                            'Способ_упаковки': None,
                            'Личные_заметки': '',
                            'Продукт_на_сайте': None,
                            'Код_маркировки_(GTIN)': None,
                            'Номер_устройства_(MPN)': None,
                            'Идентификатор_товара': '',
                            'Уникальный_идентификатор': None,
                            'Идентификатор_подраздела': None,
                            'Идентификатор_группы': '',
                            'Подарки': None,
                            'ID_Подарков': None,
                            'Сопутствующие': None,
                            'ID_Сопутствующих': None,
                            'ID_группы_разновидностей': None,
                            'Название_Характеристики': None,
                            'Измерение_Характеристики': None,
                            'Значение_Характеристики': None,
                            'Ссылка_на_товар_на_сайте': None,
                        }
                    )

                    print(f'Обработано: {product_url}')

                save_excel(data=result_data, category_name=category_name)

                with open('data/images_urls_list.txt', 'a', encoding='utf-8') as file:
                    print(*image_url_list, file=file, sep='\n')


def save_excel(data: list[dict], category_name: str) -> None:
    """
    Сохраняет список данных в Excel-файл.

    :param data: Список словарей с данными о продавцах
    """
    directory = 'results'
    file_path = f'{directory}/result_data_{category_name}.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        # Создаем пустой файл
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Export Products Sheet', index=False)

    df_existing = read_excel(file_path, sheet_name='Export Products Sheet')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0),
                        sheet_name='Export Products Sheet', index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


def download_imgs(file_path: str, headers: dict) -> None:   # Сохраняем список ссылок в JSON
    directory = 'images'
    os.makedirs(directory, exist_ok=True)

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, image_url in enumerate(image_urls_list, 1):
        image_title = image_url.split('/')[-1]

        with Session() as session:
            time.sleep(1)
            response = session.get(url=image_url, headers=headers)

        with open(f'{directory}/{image_title}', 'wb') as file:
            file.write(response.content)

        print(f'Обработано изображений: {k}/{count_urls}')


def main():
    """
    Главная функция:
    1. Загружает список товаров из JSON
    2. Собирает данные по каждому товару
    3. Сохраняет результат в Excel
    """
    # product_data_list = get_products_urls(category_dict=category_dict, headers=headers)
    get_products_data(file_path='data/product_data_list.json')
    download_imgs(file_path="data/images_urls_list.txt", headers=headers)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
