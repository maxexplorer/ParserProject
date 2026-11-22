# update_volume.py

import pandas as pd
import openpyxl

from excel_io import find_workbook, save_workbook

from configs.config import API_URLS_OZON, OZON_HEADERS
from api_requests import ApiError, read_json, send_request


def load_offer_id_from_excel(sheet_name: str) -> list[str]:
    """
    Загружает offer_id из Excel (2-й столбец), начиная с 3 строки (skiprows=2).
    Возвращает список offer_id.
    """
    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return []

    # читаем Excel
    df = pd.read_excel(source, sheet_name=sheet_name, skiprows=2, dtype=str)
    df.columns = df.columns.str.strip()

    offer_ids = []

    for _, row in df.iterrows():
        offer_id = str(row.iloc[1]).strip()  # 2-й столбец
        if offer_id and offer_id.lower() != 'nan':
            offer_ids.append(offer_id)

    return offer_ids


def get_volume_ozon(offer_ids: list[str]) -> dict:
    """
    Запрашивает габариты товаров по API v4/product/info/attributes
    и вычисляет объем (м³) по формуле height * depth * width / 1_000_000.
    Возвращает словарь {offer_id: volume_m3}
    """
    result = {}

    data = {
        'filter': {
            'offer_id': offer_ids,
            'visibility': 'ALL'
        },
        'limit': len(offer_ids),
        'sort_dir': 'ASC'
    }

    if not offer_ids:
        return result
    label = 'Ozon (габариты)'
    response = send_request(
        'POST', API_URLS_OZON['product_info_attributes'], label=label, headers=OZON_HEADERS, json=data,
    )
    data = read_json(response, label)
    items = data['result']
    if not isinstance(items, list) or data.get('total', len(items)) > len(items):
        raise ApiError(f'{label}: некорректный список товаров.')

    for item in items:
        offer_id = item.get('offer_id')
        if not offer_id:
            continue

        volume = (item['height'] * item['depth'] * item['width']) / 1_000_000

        result[offer_id] = round(volume, 5)

    return result


def write_volume_to_excel(volume_data: dict, marketplace='ОЗОН') -> None:
    """
    Записывает объем (м³) в 15-й столбец Excel.
    Старт записи — с 4-й строки (как и цены).
    """
    source = find_workbook()
    if source is None:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return

    wb = openpyxl.load_workbook(source)
    if marketplace not in wb.sheetnames:
        print(f'❗ Лист {marketplace} не найден.')
        return

    ws = wb[marketplace]

    for row in ws.iter_rows(min_row=4):
        offer_id = str(row[1].value).strip()
        if not offer_id:
            continue

        volume_value = volume_data.get(offer_id)
        if volume_value is not None:
            ws.cell(row=row[1].row, column=15, value=round(volume_value, 2))

    save_workbook(wb)
    print("✅ Объемы успешно записаны в Excel (15-й столбец)")
