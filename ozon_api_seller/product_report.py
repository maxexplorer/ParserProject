import time
from datetime import datetime

import requests

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import process_and_save_excel_from_csv_content

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
}


def create_products_report(headers: dict) -> str | None:
    data = {
        'language': 'RU',
        'offer_id': [],
        'search': '',
        'sku': [],
        'visibility': 'ALL'
    }

    try:
        response = requests.post(
            API_URLS.get('report_products_create'),
            headers=headers,
            json=data,
            timeout=10)
        response.raise_for_status()
        data = response.json()
        code = data.get('result', {}).get('code')
        return code
    except requests.exceptions.RequestException as e:
        print(f'❌ Ошибка при создании отчёта: {e}')
    except ValueError:
        print('❌ Ошибка при обработке JSON-ответа.')
    except Exception as e:
        print(f'❌ Общая ошибка: {e}')

    return None


def get_report_file_link(headers: dict, report_code: str) -> str | None:
    try:
        response = requests.post(
            API_URLS.get('report_info'),
            headers=headers,
            json={'code': report_code},
            timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get('result', {})
        if result.get('status') == 'success':
            return result.get('file')
        else:
            print(f'⏳ Статус отчёта: {result.get("status")}')
    except requests.exceptions.RequestException as e:
        print(f'❌ Ошибка при получении отчёта: {e}')
    except ValueError:
        print('❌ Ошибка при декодировании JSON-ответа.')

    return None


def run_product_report() -> None:
    print('📨 Запрашиваем отчёт по товарам...')
    report_code = create_products_report(headers=headers)
    if not report_code:
        return

    print('⏱ Ожидаем готовность отчёта...')
    for attempt in range(10):
        time.sleep(5)
        file_url = get_report_file_link(headers, report_code)
        if file_url:
            print('✅ Отчёт готов, загружаем и обрабатываем...')

            try:
                resp = requests.get(file_url, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f'❌ Ошибка загрузки CSV: {e}')
                return

            csv_str = resp.content.decode('utf-8')

            process_and_save_excel_from_csv_content(csv_str)
            return

        print(f'🔁 Попытка {attempt + 1}/10: отчёт не готов.')

    print('❗ Отчёт не был готов вовремя.')
