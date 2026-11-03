import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from pandas import DataFrame, ExcelWriter
from requests import Session

from data.data import category_data_list


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / 'data' / 'section_data_list.json'
RESULTS_DIR = BASE_DIR / 'results'
SHEET_NAME = 'Export Products Sheet'
BASE_URL = 'https://utz74.ru'

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

MODEL_PATTERNS = [
    (re.compile(r'\b[ТT]\s*[-–—]?\s*(130|170)\b', re.IGNORECASE), 'Т-{}'),
    (re.compile(r'\bБ\s*[-–—]?\s*(10|170)\b', re.IGNORECASE), 'Б-{}'),
    (re.compile(r'\bД\s*[-–—]?\s*(160|180)\b', re.IGNORECASE), 'Д-{}'),
]


def clean_text(value: str) -> str:
    return ' '.join(value.replace('\xa0', ' ').split())


def normalize_header(value: str) -> str:
    return clean_text(value).casefold().replace('ё', 'е')


def get_html(
    url: str,
    session: Session,
    retries: int = 3,
) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url=url, headers=HEADERS, timeout=90)
            response.raise_for_status()
            return response.text
        except Exception as error:
            print(f'Ошибка запроса {url} ({attempt}/{retries}): {error}')
            if attempt < retries:
                time.sleep(attempt * 3)

    return None


def is_section_url(url: str, category_url: str) -> bool:
    parsed_url = urlparse(url)
    parsed_category = urlparse(category_url)
    path = parsed_url.path.strip('/')

    if parsed_url.netloc.casefold() != parsed_category.netloc.casefold():
        return False
    if not path or '/' in path:
        return False
    if url.rstrip('/') == category_url.rstrip('/'):
        return False
    if path in {
        'catalog',
        'contact-us',
        'about-us',
        'specials',
        'oplata',
        'dostavka',
        'vozvrat-obmen',
        'kontakty',
    }:
        return False
    if path.startswith(('news', 'zapchasti-', 'katalog-', 'price')):
        return False

    return True


def parse_section_urls(html: str, category_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'lxml')
    heading = soup.find(
        ['h1', 'h2'],
        string=lambda text: bool(
            text and 'каталог запчастей т-130' in normalize_header(text)
        ),
    )
    if heading is None:
        heading = soup.find('h1')
    if heading is None:
        raise ValueError('Не найден заголовок каталога сборочных схем')

    section_urls: list[str] = []
    for element in heading.find_all_next():
        if not isinstance(element, Tag):
            continue

        if element.name in {'h1', 'h2', 'h3', 'h4'}:
            element_text = normalize_header(element.get_text(' ', strip=True))
            if 'наши новости' in element_text:
                break

        if element.name != 'a':
            continue

        href = element.get('href', '')
        if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            continue

        section_url = urljoin(category_url, href).split('#', 1)[0]
        if is_section_url(section_url, category_url) and section_url not in section_urls:
            section_urls.append(section_url)

    return section_urls


def find_table_columns(table: Tag) -> tuple[dict[str, int], int] | None:
    for row_index, row in enumerate(table.select('tr')):
        cells = row.find_all(['th', 'td'])
        headers = [normalize_header(cell.get_text(' ', strip=True)) for cell in cells]
        article_index = next(
            (index for index, value in enumerate(headers) if 'артикул' in value),
            None,
        )
        name_index = next(
            (index for index, value in enumerate(headers) if 'наименование' in value),
            None,
        )
        if article_index is None or name_index is None:
            continue

        columns = {
            'article': article_index,
            'name': name_index,
        }
        for index, value in enumerate(headers):
            if value.startswith('поз'):
                columns['position'] = index
            elif 'кол-во' in value or 'количество' in value:
                columns['quantity'] = index
            elif 'входит в сборку' in value:
                columns['assembly'] = index

        return columns, row_index

    return None


def get_cell(cells: list[Tag], index: int | None) -> str:
    if index is None or index >= len(cells):
        return ''
    return clean_text(cells[index].get_text(' ', strip=True))


def find_section_image(table: Tag, category_url: str) -> str:
    image = table.find_previous('img', src=True)
    if image is None:
        return ''

    source = image.get('data-src') or image.get('src') or ''
    lowered_source = source.casefold()
    if any(marker in lowered_source for marker in ('logo', 'icon', 'pixel', 'yandex')):
        return ''

    return urljoin(category_url, source)


def extract_models(text: str, default_models: list[str]) -> list[str]:
    models: list[str] = []

    for pattern, template in MODEL_PATTERNS:
        for match in pattern.finditer(text):
            model = template.format(match.group(1).upper())
            if model not in models:
                models.append(model)

    return models or default_models


def build_search_queries(
    name: str,
    sku: str,
    search_text: str,
    category_data: dict[str, Any],
) -> str:
    queries: list[str] = []
    detected_models = extract_models(search_text, [])
    models = list(category_data.get('required_models', []))
    for model in detected_models or category_data.get('default_models', []):
        if model not in models:
            models.append(model)
    templates = category_data.get('search_query_templates', [])

    for model in models:
        for template in templates:
            query = clean_text(template.format(model=model))
            if query and query.casefold() not in {item.casefold() for item in queries}:
                queries.append(query)

    for query in (name, sku):
        query = clean_text(query)
        if query and query.casefold() not in {item.casefold() for item in queries}:
            queries.append(query)

    return ', '.join(queries)


def build_description(
    section_name: str,
    position: str,
    quantity: str,
    assembly: str,
) -> str:
    parts = [f'Сборка: {section_name}']
    if position:
        parts.append(f'Позиция на схеме: {position}')
    if quantity:
        parts.append(f'Количество в сборке: {quantity}')
    if assembly:
        parts.append(f'Входит в сборку: {assembly}')
    return '; '.join(parts)


def parse_section_page(
    html: str,
    section_url: str,
    category_data: dict[str, Any],
) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, 'lxml')
    heading = soup.find('h1')
    section_name = (
        clean_text(heading.get_text(' ', strip=True))
        if heading is not None
        else section_url.rstrip('/').rsplit('/', 1)[-1]
    )
    products: list[dict[str, Any]] = []

    for table in soup.find_all('table'):
        table_columns = find_table_columns(table)
        if table_columns is None:
            continue

        columns, header_row_index = table_columns
        image_url = find_section_image(table, section_url)
        rows = table.select('tr')

        for row in rows[header_row_index + 1:]:
            cells = row.find_all('td')
            if not cells:
                continue

            sku = get_cell(cells, columns.get('article'))
            item_name = get_cell(cells, columns.get('name'))
            if not sku or not item_name:
                continue

            name = item_name if sku.casefold() in item_name.casefold() else f'{item_name} {sku}'
            position = get_cell(cells, columns.get('position'))
            quantity = get_cell(cells, columns.get('quantity'))
            assembly = get_cell(cells, columns.get('assembly'))
            search_text = f'{name} {section_name}'

            products.append(
                {
                    'name': name,
                    'sku': sku,
                    'description': build_description(
                        section_name,
                        position,
                        quantity,
                        assembly,
                    ),
                    'image_url': image_url,
                    'search_queries': build_search_queries(
                        name,
                        sku,
                        search_text,
                        category_data,
                    ),
                    'section_url': section_url,
                }
            )

    return products


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


def save_section_urls(section_data: list[dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open('w', encoding='utf-8') as file:
        json.dump(section_data, file, indent=4, ensure_ascii=False)


def resolve_group_number(
    category_data: dict[str, Any],
    group_number_override: int | None,
) -> int | None:
    if group_number_override is not None:
        return group_number_override

    environment_value = os.getenv('UTZ74_GROUP_NUMBER', '').strip()
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
    category_url = category_data['category_url']
    catalog_html = get_html(category_url, session)
    if not catalog_html:
        raise ConnectionError(f'Не удалось загрузить каталог: {category_url}')

    section_urls = parse_section_urls(catalog_html, category_url)
    if not section_urls:
        raise ValueError('В каталоге не найдены ссылки на сборочные схемы')
    group_number = resolve_group_number(category_data, group_number_override)
    result_data: list[dict[str, Any]] = []
    seen_skus: set[str] = set()

    for index, section_url in enumerate(section_urls, 1):
        if index > 1:
            time.sleep(delay)
        html = get_html(section_url, session)
        if not html:
            continue

        for product in parse_section_page(html, section_url, category_data):
            sku_key = product['sku'].casefold()
            if sku_key in seen_skus:
                continue
            seen_skus.add(sku_key)
            result_data.append(build_export_row(product, group_number))

            if limit is not None and len(result_data) >= limit:
                break

        print(
            f'Разделы {index}/{len(section_urls)}: '
            f'собрано {len(result_data)} уникальных деталей'
        )
        if limit is not None and len(result_data) >= limit:
            break

    if not result_data:
        raise ValueError('В сборочных схемах не найдены таблицы деталей')

    return section_urls, result_data


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Парсер каталога запчастей Т-130/Т-170 с utz74.ru',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='ограничить число деталей (удобно для проверки)',
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
    all_section_data: list[dict[str, Any]] = []

    with Session() as session:
        for category_data in category_data_list:
            section_urls, result_data = parse_category(
                session=session,
                category_data=category_data,
                delay=arguments.delay,
                limit=arguments.limit,
                group_number_override=arguments.group_number,
            )
            all_section_data.append(
                {
                    'category_name': category_data['category_name'],
                    'group_number': resolve_group_number(
                        category_data,
                        arguments.group_number,
                    ),
                    'section_urls': section_urls,
                }
            )
            save_excel(result_data, category_data['category_name'])

    save_section_urls(all_section_data)
    print(f'Сбор данных завершён за {datetime.now() - start_time}')


if __name__ == '__main__':
    main()
