import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from pandas import DataFrame, ExcelWriter
from requests import Session

from data.data import category_data_list


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / 'data' / 'product_data_list.json'
RESULTS_DIR = BASE_DIR / 'results'
SHEET_NAME = 'Export Products Sheet'

HEADERS: dict[str, str] = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/140.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9',
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


def clean_text(value: str) -> str:
    return ' '.join(value.replace('\xa0', ' ').split())


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


def parse_section_urls(html: str, category_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, 'lxml')
    sections: list[dict[str, str]] = []

    for section_item in soup.select('.spares-item.subs'):
        link = section_item.select_one('.spares-item-sub-name a[href]')
        if link is None:
            continue

        section_url = urljoin(category_url, link.get('href', ''))
        section_name = clean_text(link.get_text(' ', strip=True))
        if section_url and section_url not in {item['url'] for item in sections}:
            sections.append({'name': section_name, 'url': section_url})

    return sections


def parse_product_urls(
    html: str,
    section_url: str,
    section_name: str,
) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, 'lxml')
    products: list[dict[str, str]] = []

    for product_item in soup.select('.parts-item'):
        link = product_item.select_one('.parts-name a[itemprop="url"][href]')
        if link is None:
            continue

        product_url = urljoin(section_url, link.get('href', ''))
        if product_url and product_url not in {item['url'] for item in products}:
            products.append(
                {
                    'url': product_url,
                    'section_name': section_name,
                }
            )

    return products


def collect_product_urls(
    session: Session,
    category_url: str,
    delay: float,
    limit: int | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    category_html = get_html(category_url, session)
    if not category_html:
        raise ConnectionError(f'Не удалось загрузить каталог: {category_url}')

    sections = parse_section_urls(category_html, category_url)
    if not sections:
        raise ValueError('В каталоге не найдены разделы ДЗ-98')

    product_urls: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for index, section in enumerate(sections, 1):
        if index > 1:
            time.sleep(delay)
        html = get_html(section['url'], session)
        if not html:
            continue

        for product_data in parse_product_urls(
            html,
            section['url'],
            section['name'],
        ):
            if product_data['url'] in seen_urls:
                continue
            seen_urls.add(product_data['url'])
            product_urls.append(product_data)
            if limit is not None and len(product_urls) >= limit:
                break

        print(
            f'Разделы {index}/{len(sections)}: '
            f'собрано {len(product_urls)} ссылок'
        )
        if limit is not None and len(product_urls) >= limit:
            break

    if not product_urls:
        raise ValueError('В разделах ДЗ-98 не найдены товары')

    return sections, product_urls


def html_to_description(features_html: str) -> str:
    if not features_html:
        return ''

    soup = BeautifulSoup(features_html, 'lxml')
    parts: list[str] = []

    for table in soup.find_all('table'):
        rows = [
            [
                clean_text(cell.get_text(' ', strip=True))
                for cell in row.find_all(['th', 'td'])
            ]
            for row in table.select('tr')
        ]
        rows = [row for row in rows if row]
        if not rows:
            continue

        if all(len(row) == 2 for row in rows):
            for name, value in rows:
                if name and value:
                    pair = f"{name.rstrip(':')}: {value}"
                    if pair not in parts:
                        parts.append(pair)
        elif len(rows) >= 2:
            headers = [header.rstrip(':') for header in rows[0]]
            for values in rows[1:]:
                for header, value in zip(headers, values):
                    if header and value:
                        pair = f'{header}: {value}'
                        if pair not in parts:
                            parts.append(pair)

        table.decompose()

    remaining_text = clean_text(soup.get_text(' ', strip=True))
    if remaining_text:
        parts.insert(0, remaining_text)

    return '; '.join(parts)


def build_search_queries(
    name: str,
    nomenclature: str,
    category_data: dict[str, Any],
) -> str:
    queries: list[str] = []

    for model in category_data.get('required_models', []):
        for template in category_data.get('search_query_templates', []):
            query = clean_text(template.format(model=model))
            if query and query.casefold() not in {item.casefold() for item in queries}:
                queries.append(query)

    for query in (name, nomenclature):
        query = clean_text(query)
        if not query:
            continue
        if query.casefold() in name.casefold() and query != name:
            continue
        if query.casefold() not in {item.casefold() for item in queries}:
            queries.append(query)

    return ', '.join(queries)


def parse_product_card(
    html: str,
    product_url: str,
    category_data: dict[str, Any],
) -> dict[str, Any]:
    soup = BeautifulSoup(html, 'lxml')
    product_data_node = soup.select_one('#ms-product-data')
    if product_data_node is None or not product_data_node.string:
        raise ValueError(f'Не найден JSON товара: {product_url}')

    page_data = json.loads(product_data_node.string)
    product = page_data.get('product')
    if not product:
        raise ValueError(f'Страница не является товаром: {product_url}')

    name = clean_text(product.get('name', ''))
    nomenclature = clean_text(product.get('nomenclature', ''))
    identifier = nomenclature or str(product.get('code') or product.get('id') or name)
    media = product.get('media') or {}
    content = product.get('content') or {}
    availability = product.get('availability') or {}

    return {
        'name': name,
        'sku': identifier,
        'description': html_to_description(content.get('features_html', '')),
        'image_url': media.get('image_main', '') or '',
        'availability': '+' if availability.get('in_stock', True) else '-',
        'search_queries': build_search_queries(
            name,
            nomenclature,
            category_data,
        ),
        'product_url': product_url,
    }


def load_product(
    product_data: dict[str, str],
    category_data: dict[str, Any],
    delay: float,
) -> dict[str, Any] | None:
    if delay:
        time.sleep(delay)

    with Session() as session:
        html = get_html(product_data['url'], session)
    if not html:
        return None

    try:
        return parse_product_card(html, product_data['url'], category_data)
    except (ValueError, json.JSONDecodeError) as error:
        print(error)
        return None


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
        'Наличие': product['availability'],
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

    environment_value = os.getenv('MS74_GROUP_NUMBER', '').strip()
    if environment_value:
        return int(environment_value)

    return category_data.get('group_number')


def parse_category(
    session: Session,
    category_data: dict[str, Any],
    delay: float,
    limit: int | None,
    workers: int,
    group_number_override: int | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, Any]]]:
    sections, product_urls = collect_product_urls(
        session,
        category_data['category_url'],
        delay,
        limit,
    )
    group_number = resolve_group_number(category_data, group_number_override)
    result_data: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        products = executor.map(
            lambda item: load_product(item, category_data, delay),
            product_urls,
        )
        for index, product in enumerate(products, 1):
            if product is not None:
                result_data.append(build_export_row(product, group_number))
            print(f'Карточки: {index}/{len(product_urls)}')

    if not result_data:
        raise ValueError('Не удалось обработать карточки товаров ДЗ-98')

    return sections, product_urls, result_data


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Парсер запчастей ДЗ-98 с ms-74.ru',
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
        default=0.2,
        help='пауза перед запросами в секундах (по умолчанию: 0.2)',
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='число одновременных запросов карточек (по умолчанию: 4)',
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
    if arguments.workers < 1:
        raise ValueError('--workers должен быть больше нуля')

    start_time = datetime.now()
    all_product_data: list[dict[str, Any]] = []

    with Session() as session:
        for category_data in category_data_list:
            sections, product_urls, result_data = parse_category(
                session=session,
                category_data=category_data,
                delay=arguments.delay,
                limit=arguments.limit,
                workers=arguments.workers,
                group_number_override=arguments.group_number,
            )
            all_product_data.append(
                {
                    'category_name': category_data['category_name'],
                    'group_number': resolve_group_number(
                        category_data,
                        arguments.group_number,
                    ),
                    'sections': sections,
                    'product_urls': product_urls,
                }
            )
            save_excel(result_data, category_data['category_name'])

    save_product_urls(all_product_data)
    print(f'Сбор данных завершён за {datetime.now() - start_time}')


if __name__ == '__main__':
    main()
