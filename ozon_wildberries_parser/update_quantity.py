# update_quantity.py

import os
import glob

import requests
import openpyxl

from configs.config import API_URLS_OZON, OZON_HEADERS


def get_fbs_quantity_ozon(offer_ids: list[str]) -> dict:
    """
    Получает остатки FBS по списку offer_id.
    Возвращает словарь:
    {
        offer_id: fbs_present,
        ...
    }
    """

    result = {}

    cursor = ''
    limit = 100

    while True:
        payload = {
            'cursor': cursor,
            'filter': {
                'visibility': 'ALL',
                'offer_id': offer_ids
            },
            'limit': limit
        }

        try:
            response = requests.post(
                API_URLS_OZON['product_info_stocks'],
                headers=OZON_HEADERS,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            print(f'❌ Ошибка API: {e}')
            break

        data = response.json()

        items = data.get('items', [])

        for item in items:
            offer = item.get('offer_id')
            if not offer:
                continue

            stocks = item.get('stocks', [])

            for stock in stocks:
                s_type = stock.get('type', '').lower()
                if s_type == 'fbs':
                    result[offer] = stock.get('present', 0)

        cursor = data.get('cursor')
        if not cursor:
            break

    return result


def write_fbs_quantity_to_excel(fbs_data: dict, marketplace='ОЗОН') -> None:
    """
    Записывает остатки FBS в 16-й столбец Excel.
    Старт записи — с 4-й строки.
    """

    folder = 'data'
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return

    wb = openpyxl.load_workbook(excel_files[0])
    if marketplace not in wb.sheetnames:
        print(f'❗ Лист {marketplace} не найден.')
        return

    ws = wb[marketplace]

    for row in ws.iter_rows(min_row=4):
        offer_id = str(row[1].value).strip()
        if not offer_id:
            continue

        fbs_value = fbs_data.get(offer_id)
        if fbs_value is not None:
            row[15].value = fbs_value      # 16-й столбец (индекс 15)

    wb.save(os.path.join(folder, 'data.xlsx'))
    print('✅ Остатки FBS успешно записаны в Excel (16-й столбец)')


# Для ручного теста
if __name__ == '__main__':
    pass
