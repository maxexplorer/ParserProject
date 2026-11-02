import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter
from requests import Session

from data.data import category_data_list


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / 'data' / 'product_data_list.json'
RESULTS_DIR = BASE_DIR / 'results'
SHEET_NAME = 'Export Products Sheet'
BASE_URL = 'https://agrobaza74.ru'

HEADERS: dict[str, str] = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/140.0.0.0 Safari/537.36'
    ),
}

EXPORT_COLUMNS = [
    'Код_товара',
    'Название_позиции',
    'Поисковые_запросы',
    'Описание',
    'Тип_товара',
    'Цена',
    'Цена от',
    'Ярлык',
    'HTML_заголовок',
    'HTML_описание',
    'HTML_ключевые_слова',
    'Валюта',
    'Скидка',
    'Cрок действия скидки от',
    'Cрок действия скидки до',
    'Единица_измерения',
    'Минимальный_объем_заказа',
    'Оптовая_цена',
    'Минимальный_заказ_опт',
    'Ссылка_изображения',
    'Наличие',
    'Количество',
    'Производитель',
    'Страна_производитель',
    'Номер_группы',
    'Адрес_подраздела',
    'Возможность_поставки',
    'Срок_поставки',
    'Способ_упаковки',
    'Личные_заметки',
    'Продукт_на_сайте',
    'Код_маркировки_(GTIN)',
    'Номер_устройства_(MPN)',
    'Идентификатор_товара',
    'Уникальный_идентификатор',
    'Идентификатор_подраздела',
    'Идентификатор_группы',
    'Подарки',
    'ID_Подарков',
    'Сопутствующие',
    'ID_Сопутствующих',
    'ID_группы_разновидностей',
    'Название_Характеристики',
    'Измерение_Характеристики',
    'Значение_Характеристики',
    'Ссылка_на_товар_на_сайте',
]

MODEL_PATTERN = re.compile(
    r'\b[КK]\s*[-–—]?\s*(700А?|701М?|702|703|744(?:Р\d?)?)\b',
    re.IGNORECASE,
)


def clean_text(value: str) -> str:
    return ' '.join(value.split())


def get_html(
    url: str,
    session: Session,
    retries: int = 3,
) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url=url, headers=HEADERS, timeout=60)
            response.raise_for_status()
            return response.text
        except Exception as error:
            print(f'Ошибка запроса {url} ({attempt}/{retries}): {error}')
            if attempt < retries:
                time.sleep(attempt * 2)

    return None


def page_position(url: str) -> int:
    values = parse_qs(urlparse(url).query).get('curPos', ['0'])
    try:
        return int(values[0])
    except (TypeError, ValueError):
        return 0


def get_catalog_page_urls(html: str, category_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'lxml')
    page_urls = {category_url}

    for link in soup.select('.pagination a[href]'):
        href = link.get('href', '')
        if 'curPos=' in href:
            page_urls.add(urljoin(category_url, href))

    return sorted(page_urls, key=page_position)


def parse_catalog_page(html: str, category_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'lxml')
    product_urls: list[str] = []

    for product_item in soup.select('div.catalog-items > div.catalog-item'):
        link = product_item.select_one('.blk_name a[href]')
        if link is None:
            link = product_item.select_one('a.image-default[href]')
        if link is None:
            continue

        product_url = urljoin(category_url, link.get('href', ''))
        if product_url and product_url not in product_urls:
            product_urls.append(product_url)

    return product_urls


def collect_product_urls(
    session: Session,
    category_url: str,
    delay: float,
    limit: int | None = None,
) -> list[str]:
    first_page_html = get_html(category_url, session)
    if not first_page_html:
        return []

    page_urls = get_catalog_page_urls(first_page_html, category_url)
    product_urls: list[str] = []

    for page_index, page_url in enumerate(page_urls, 1):
        if page_index == 1 and page_url == category_url:
            html = first_page_html
        else:
            time.sleep(delay)
            html = get_html(page_url, session)

        if not html:
            continue

        for product_url in parse_catalog_page(html, category_url):
            if product_url not in product_urls:
                product_urls.append(product_url)
            if limit is not None and len(product_urls) >= limit:
                break

        print(
            f'Страница каталога {page_index}/{len(page_urls)}: '
            f'собрано {len(product_urls)} ссылок'
        )
        if limit is not None and len(product_urls) >= limit:
            break

    return product_urls


def extract_models(name: str, default_models: list[str]) -> list[str]:
    models: list[str] = []
    for match in MODEL_PATTERN.finditer(name):
        model = f"К-{match.group(1).upper()}"
        if model not in models:
            models.append(model)

    return models or default_models


def build_search_queries(
    name: str,
    sku: str,
    category_data: dict[str, Any],
) -> str:
    queries: list[str] = []
    models = extract_models(name, category_data.get('default_models', []))
    templates = category_data.get('search_query_templates', [])

    for model in models:
        for template in templates:
            query = clean_text(template.format(model=model))
            if query and query.casefold() not in {item.casefold() for item in queries}:
                queries.append(query)

    for query in (name, sku):
        query = clean_text(query)
        if not query:
            continue
        if query.casefold() in name.casefold() and query != name:
            continue
        if query.casefold() not in {item.casefold() for item in queries}:
            queries.append(query)

    return ', '.join(queries)


def extract_characteristics(product_item: Any) -> str:
    characteristics: list[str] = []

    for parameter in product_item.select('#cart-param-2 .cart-param-line'):
        name_item = parameter.select_one('.cartp-name')
        value_item = parameter.select_one('.cartp-value')
        if name_item is None or value_item is None:
            continue

        name = clean_text(name_item.get_text(' ', strip=True)).rstrip(':')
        value = clean_text(value_item.get_text(' ', strip=True))
        if name and value:
            characteristics.append(f'{name}: {value}')

    return '; '.join(characteristics)


def parse_product_card(
    html: str,
    product_url: str,
    category_data: dict[str, Any],
) -> dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    product_item = soup.select_one('.itemcard.catalog-item-full')
    if product_item is None:
        raise ValueError(f'Не найдена карточка товара: {product_url}')

    name_item = product_item.select_one('h1.title')
    sku_item = product_item.select_one('.art_value_full')
    code_item = product_item.select_one('.art2_value_full')
    image_item = product_item.select_one('.owl-incard a.image-default[href]')

    name = clean_text(name_item.get_text(' ', strip=True)) if name_item else ''
    sku = clean_text(sku_item.get_text(' ', strip=True)) if sku_item else ''
    code = clean_text(code_item.get_text(' ', strip=True)) if code_item else ''

    image_url = ''
    if image_item is not None:
        image_url = urljoin(BASE_URL, image_item.get('href', ''))
    if not image_url:
        open_graph_image = soup.select_one('meta[property="og:image"][content]')
        if open_graph_image is not None:
            image_url = urljoin(BASE_URL, open_graph_image.get('content', ''))

    identifier = sku or code or name

    return {
        'name': name,
        'sku': identifier,
        'description': extract_characteristics(product_item),
        'image_url': image_url,
        'search_queries': build_search_queries(name, identifier, category_data),
        'product_url': product_url,
    }


def build_export_row(
    product: dict[str, Any],
    group_number: int | None,
) -> dict[str, Any]:
    return {
        'Код_товара': None,
        'Название_позиции': product['name'],
        'Поисковые_запросы': product['search_queries'],
        'Описание': product['description'],
        'Тип_товара': 'u',
        'Цена': '',
        'Цена от': None,
        'Ярлык': None,
        'HTML_заголовок': None,
        'HTML_описание': None,
        'HTML_ключевые_слова': None,
        'Валюта': '',
        'Скидка': '',
        'Cрок действия скидки от': None,
        'Cрок действия скидки до': None,
        'Единица_измерения': '',
        'Минимальный_объем_заказа': None,
        'Оптовая_цена': None,
        'Минимальный_заказ_опт': None,
        'Ссылка_изображения': product['image_url'],
        'Наличие': '+',
        'Количество': None,
        'Производитель': None,
        'Страна_производитель': None,
        'Номер_группы': group_number,
        'Адрес_подраздела': None,
        'Возможность_поставки': None,
        'Срок_поставки': None,
        'Способ_упаковки': None,
        'Личные_заметки': '',
        'Продукт_на_сайте': None,
        'Код_маркировки_(GTIN)': None,
        'Номер_устройства_(MPN)': None,
        'Идентификатор_товара': product['sku'],
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


def safe_file_name(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', '_', value).strip(' .')


def save_excel(data: list[dict[str, Any]], category_name: str) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = RESULTS_DIR / f'result_data_{safe_file_name(category_name)}.xlsx'
    data_frame = DataFrame(data, columns=EXPORT_COLUMNS)

    with ExcelWriter(file_path, mode='w', engine='openpyxl') as writer:
        data_frame.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')
    return file_path


def save_product_urls(product_data: list[dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open('w', encoding='utf-8') as file:
        json.dump(product_data, file, indent=4, ensure_ascii=False)


def resolve_group_number(
    category_data: dict[str, Any],
    group_number_override: int | None,
) -> int | None:
    if group_number_override is not None:
        return group_number_override

    environment_value = os.getenv('AGROBAZA_GROUP_NUMBER', '').strip()
    if environment_value:
        return int(environment_value)

    return category_data.get('group_number')


def parse_category(
    session: Session,
    category_data: dict[str, Any],
    delay: float,
    limit: int | None,
    group_number_override: int | None,
) -> tuple[list[str], list[dict[str, Any]]]:
    category_name = category_data['category_name']
    category_url = category_data['category_url']
    group_number = resolve_group_number(category_data, group_number_override)
    product_urls = collect_product_urls(session, category_url, delay, limit)
    result_data: list[dict[str, Any]] = []

    for index, product_url in enumerate(product_urls, 1):
        if index > 1:
            time.sleep(delay)
        html = get_html(product_url, session)
        if not html:
            continue

        try:
            product = parse_product_card(html, product_url, category_data)
        except ValueError as error:
            print(error)
            continue

        if not product['name']:
            print(f'Пропущен товар без названия: {product_url}')
            continue

        result_data.append(build_export_row(product, group_number))
        print(f'Карточки {category_name}: {index}/{len(product_urls)}')

    return product_urls, result_data


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Парсер запчастей К-700/К-744 с agrobaza74.ru',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='ограничить число товаров (удобно для проверки)',
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='пауза между запросами в секундах (по умолчанию: 0.5)',
    )
    parser.add_argument(
        '--group-number',
        type=int,
        default=None,
        help='номер группы для загрузки на сайт клиента',
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.limit is not None and arguments.limit < 1:
        raise ValueError('--limit должен быть больше нуля')
    if arguments.delay < 0:
        raise ValueError('--delay не может быть отрицательной')

    start_time = datetime.now()
    all_product_data: list[dict[str, Any]] = []

    with Session() as session:
        for category_data in category_data_list:
            product_urls, result_data = parse_category(
                session=session,
                category_data=category_data,
                delay=arguments.delay,
                limit=arguments.limit,
                group_number_override=arguments.group_number,
            )
            all_product_data.append(
                {
                    'category_name': category_data['category_name'],
                    'group_number': resolve_group_number(
                        category_data,
                        arguments.group_number,
                    ),
                    'product_urls': product_urls,
                }
            )
            save_excel(result_data, category_data['category_name'])

    save_product_urls(all_product_data)
    print(f'Сбор данных завершён за {datetime.now() - start_time}')


if __name__ == '__main__':
    main()
