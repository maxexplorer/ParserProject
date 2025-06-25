import time
from datetime import datetime
import requests

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_csv, prepare_excel_from_csv
from data.data import COLUMN_MAPPING, TARGET_COLUMNS

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
}


def create_products_report(headers: dict) -> str | None:
    """
    Запрашивает создание отчёта по всем товарам.

    :param headers: Заголовки с Client-Id и Api-Key
    :return: Строка с кодом отчёта или None
    """
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
    """
    Получает ссылку на файл отчёта по коду.

    :param headers: Заголовки с Client-Id и Api-Key
    :param report_code: Код отчёта
    :return: Ссылка на файл или None
    """
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
    """
    Основная функция:
    - создаёт отчёт
    - ожидает его готовность
    - получает ссылку на CSV
    - сохраняет и форматирует в Excel
    """
    print('📨 Запрашиваем отчёт по товарам...')
    report_code = create_products_report(headers=headers)
    if not report_code:
        return

    print('⏱ Ожидаем готовность отчёта...')
    for attempt in range(10):
        time.sleep(5)
        file_url = get_report_file_link(headers, report_code)
        if file_url:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            csv_path = f'results/ozon_products_{timestamp}.csv'
            excel_path = f'results/ozon_products_{timestamp}.xlsx'

            save_csv(file_url, csv_path)
            prepare_excel_from_csv(csv_path, excel_path, COLUMN_MAPPING, TARGET_COLUMNS)
            return

        print(f'🔁 Попытка {attempt + 1}/10: отчёт не готов.')

    print('❗ Отчёт не был готов вовремя.')
