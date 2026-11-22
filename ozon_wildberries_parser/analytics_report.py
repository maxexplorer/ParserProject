# analytics_report.py

from datetime import datetime, timedelta

import pandas as pd
import openpyxl

from excel_io import DATA_WORKBOOK, find_workbook, save_workbook

from configs.config import API_URLS_OZON, OZON_HEADERS, API_URLS_WB
from api_requests import ApiError, read_json, send_request, wb_json


def load_sku_article_from_excel(sheet_name: str) -> dict:
    """
    Загружает артикулы и new_price из Excel, начиная с 3 строки (skiprows=2).
    Артикул в 1 столбце, new_price в 6 столбце.
    Возвращает словарь {offer_id: delta}
    """

    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    df = pd.read_excel(source, sheet_name=sheet_name, skiprows=2)
    df.columns = df.columns.str.strip()

    article_info = {}
    for _, row in df.iterrows():
        article = str(row.iloc[1]).strip()
        if not article:
            continue

        value = row.iloc[0]
        if pd.notna(value):
            if isinstance(value, float) and value.is_integer():
                sku = str(int(value)).strip()
            else:
                sku = str(value).strip()
        else:
            sku = ''

        if pd.isna(article) or article == '' or pd.isna(sku) or sku == '':
            continue

        if sku and article:
            article_info[sku] = article

    return article_info


def get_ozon_orders_report(
        period: str,
        product_to_offer: dict,
        custom_date_from: str = None,
        custom_date_to: str = None
) -> dict:
    """
    Получение количества заказов по offer_id за месяц, неделю или произвольный период.
    product_to_offer — словарь {product_id: offer_id}.
    Для period='custom' необходимо передавать custom_date_from и custom_date_to в формате 'YYYY-MM-DD'.
    """

    if period == 'month':
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
    elif period == 'week':
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
    elif period == 'custom':
        if not custom_date_from or not custom_date_to:
            raise ValueError('Для period="custom" необходимо передать custom_date_from и custom_date_to.')
        date_from = custom_date_from
        date_to = custom_date_to
    else:
        raise ValueError('period должен быть "month", "week" или "custom"')

    data = {
        'date_from': date_from,
        'date_to': date_to,
        'metrics': ['ordered_units'],
        'dimension': ['sku', period],
        'filters': [],
        'limit': 1000,
        'offset': 0
    }

    orders = {}
    previous_page = None
    while True:
        label = 'Ozon (аналитика)'
        response = send_request(
            'POST', API_URLS_OZON['analytics_data'], label=label, headers=OZON_HEADERS, json=data
        )
        try:
            page = read_json(response, label)['result']['data']
            if not isinstance(page, list) or len(page) > data['limit'] or page == previous_page:
                raise ValueError
            for item in page:
                product_id = str(item['dimensions'][0]['id'])
                ordered_units = int(item['metrics'][0])
                offer_id = product_to_offer.get(product_id)
                orders[offer_id] = orders.get(offer_id, 0) + ordered_units
        except (KeyError, IndexError, TypeError, ValueError):
            raise ApiError(f'{label}: некорректная или повторная страница.') from None

        if len(page) < data['limit']:
            break
        previous_page = page
        data['offset'] += data['limit']

    return orders


def get_wb_orders_report(period: str, custom_date_from: str = None, custom_date_to: str = None) -> dict:
    """
    Получение количества заказов по vendorCode за месяц, неделю или произвольный период.
    Использует новый API WB: /analytics/v3/sales-funnel/products
    Возвращает словарь {vendorCode: orderCount}.
    """

    now = datetime.now()

    # Определяем даты
    if period == 'month':
        date_from = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = now.strftime('%Y-%m-%d')
    elif period == 'week':
        date_from = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        date_to = now.strftime('%Y-%m-%d')
    elif period == 'custom':
        if not custom_date_from or not custom_date_to:
            raise ValueError('Для period="custom" необходимо передать custom_date_from и custom_date_to.')
        date_from = custom_date_from
        date_to = custom_date_to
    else:
        raise ValueError('period должен быть "month", "week" или "custom"')

    limit = 1000
    offset = 0
    orders: dict[str, int] = {}

    seen = set()
    while True:
        payload = {
            "selectedPeriod": {
                "start": date_from,
                "end": date_to
            },
            "nmIds": [],  # можно оставить пустым для всех товаров
            "skipDeletedNm": True,
            "limit": limit,
            "offset": offset
        }

        data = wb_json('POST', API_URLS_WB['products'], 'analytics', json=payload)
        try:
            products = data['data']['products']
            if data.get('error', False) or not isinstance(products, list) or len(products) > limit:
                raise ValueError
            for entry in products:
                product = entry['product']
                nm_id = product['nmId']
                vendor_code = product['vendorCode']
                count = entry['statistic']['selected']['orderCount']
                if (type(nm_id) is not int or nm_id <= 0 or nm_id in seen
                        or not isinstance(vendor_code, str) or type(count) is not int or count < 0):
                    raise ValueError
                seen.add(nm_id)
                if vendor_code:
                    orders[vendor_code] = orders.get(vendor_code, 0) + count
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ApiError('Wildberries (аналитика): некорректная или повторная страница.') from None

        if len(products) < limit:
            break
        offset += limit

    return orders


def write_analytics_to_excel(
        analytics_data: dict,
        marketplace='ОЗОН',
        column_month=12,
        column_week=13,
        column_custom=14,
        period='month'
) -> None:
    """
    Записывает данные аналитики (кол-во заказов) в Excel в указанный столбец по period.

    analytics_data: {offer_id: orders_count}
    period: 'month', 'week' или 'custom' для определения в какую колонку писать
    """
    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return

    wb = openpyxl.load_workbook(source)
    if marketplace not in wb.sheetnames:
        print(f'❗ В книге нет листа "{marketplace}"')
        return

    ws = wb[marketplace]

    if period == 'month':
        target_column = column_month
    elif period == 'week':
        target_column = column_week
    elif period == 'custom':
        target_column = column_custom
    else:
        print(f'❌ Неверное значение period: {period}. Должно быть "month", "week" или "custom".')
        return

    for row in ws.iter_rows(min_row=4):
        cell_article = row[1].value
        if not cell_article:
            continue
        offer_id = str(cell_article).strip()
        if offer_id in analytics_data:
            orders_count = analytics_data[offer_id]
            ws.cell(row=row[1].row, column=target_column, value=orders_count)

    save_workbook(wb)
    print(f'✅ Данные аналитики успешно записаны в {DATA_WORKBOOK}')
