import os
import time
import requests
import pandas as pd
from datetime import datetime
from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_csv

# Заголовки
headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
}

# Целевые столбцы (по твоему последнему сообщению)
from data.data import COLUMN_MAPPING, TARGET_COLUMNS


def create_products_report(headers: dict) -> str | None:
    data = {
        'language': 'RU',
        'offer_id': [],
        'search': '',
        'sku': [],
        'visibility': 'ALL'
    }

    try:
        response = requests.post(API_URLS['report_products_create'], headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json().get('result', {}).get('code')
    except Exception as e:
        print(f'❌ Ошибка при создании отчёта: {e}')
        return None


def get_report_file_link(headers: dict, report_code: str) -> str | None:
    try:
        response = requests.post(API_URLS['report_info'], headers=headers, json={'code': report_code}, timeout=10)
        response.raise_for_status()
        result = response.json().get('result', {})
        if result.get('status') == 'success':
            return result.get('file')
        print(f'⏳ Статус отчёта: {result.get("status")}')
    except Exception as e:
        print(f'❌ Ошибка при получении ссылки: {e}')
    return None


def fetch_price_commission_data() -> list[dict]:
    result_data = []
    cursor = ''
    limit = 100

    while True:
        data = {
            'cursor': cursor,
            'filter': {
                'offer_id': [],
                'product_id': [],
                'visibility': 'ALL'
            },
            'limit': limit
        }

        try:
            time.sleep(1)
            response = requests.post(
                API_URLS['product_info_prices'],
                headers=headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'❌ Ошибка при запросе цен: {e}')
            break

        try:
            data = response.json()
        except ValueError:
            print('❌ Ошибка при декодировании JSON.')
            break

        items = data.get('items', [])
        for item in items:
            offer_id = item.get('offer_id')
            price_info = item.get('price', {})
            commissions = item.get('commissions', {})

            acquiring = item.get('acquiring', 0)

            result_data.append({
                'Артикул': offer_id,
                'Эквайринг': acquiring,
                'Вознаграждение Ozon, FBO, %': commissions.get('sales_percent_fbo', 0),
                'Логистика Ozon, минимум, FBO': commissions.get('fbo_direct_flow_trans_min_amount', 0),
                'Логистика Ozon, максимум, FBO': commissions.get('fbo_direct_flow_trans_max_amount', 0),
                'Последняя миля, FBO': commissions.get('fbo_last_mile_amount', 0),
                'Вознаграждение Ozon, FBS, %': commissions.get('sales_percent_fbs', 0),
                'Обработка отправления, минимум FBS': commissions.get('fbs_processing_min_amount', 0),
                'Обработка отправления, максимум FBS': commissions.get('fbs_processing_max_amount', 0),
                'Логистика Ozon, минимум, FBS': commissions.get('fbs_direct_flow_trans_min_amount', 0),
                'Логистика Ozon, максимум, FBS': commissions.get('fbs_direct_flow_trans_max_amount', 0),
                'Последняя миля, FBS': commissions.get('fbs_last_mile_amount', 0),
            })

        cursor = data.get('cursor', '')
        if not cursor:
            break

    return result_data


def run_product_report() -> None:
    print('📨 Запрашиваем отчёт по товарам...')
    report_code = create_products_report(headers)
    if not report_code:
        return

    print('⏱ Ожидаем готовности отчёта...')
    for attempt in range(10):
        time.sleep(5)
        file_url = get_report_file_link(headers, report_code)
        if file_url:
            break
        print(f'🔁 Попытка {attempt + 1}/10...')
    else:
        print('❌ Отчёт не был готов.')
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    csv_path = f'results/ozon_products_{timestamp}.csv'
    excel_path = f'results/ozon_products_{timestamp}.xlsx'

    # Скачиваем CSV
    save_csv(file_url, csv_path)

    # Читаем и преобразуем
    df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # Добавляем недостающие столбцы
    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = ''

    # Строковые колонки — чистим
    str_cols = ['Артикул', 'SKU', 'Ozon SKU ID', 'Штрихкод', 'Barcode', 'Объем, л', 'Объемный вес, кг']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lstrip("'").str.strip()

    # Получаем комиссии
    print('📦 Получаем комиссионные и эквайринг...')
    commission_data = fetch_price_commission_data()
    commission_df = pd.DataFrame(commission_data)

    # Добавляем отсутствующие нужные колонки в commission_df, чтобы не было ошибок
    needed_cols = [
        'Эквайринг', 'Вознаграждение Ozon, FBO, %', 'Логистика Ozon, минимум, FBO', 'Логистика Ozon, максимум, FBO', 'Последняя миля, FBO',
        'Вознаграждение Ozon, FBS, %', 'Обработка отправления, минимум FBS', 'Обработка отправления, максимум FBS',
        'Логистика Ozon, минимум, FBS', 'Логистика Ozon, максимум, FBS', 'Последняя миля, FBS'
    ]
    for col in needed_cols:
        if col not in commission_df.columns:
            commission_df[col] = 0

    # Объединяем по "Артикул"
    df = pd.merge(df, commission_df, how='left', on='Артикул')

    # Упорядочим по нужным столбцам
    df = df[TARGET_COLUMNS]

    # Сохраняем
    df.to_excel(excel_path, index=False)
    print(f'✅ Excel сохранён: {excel_path}')

