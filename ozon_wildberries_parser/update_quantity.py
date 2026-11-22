# update_quantity.py


from excel_io import DATA_WORKBOOK, open_workbook_sheet, save_workbook

from configs.config import API_URLS_OZON, OZON_HEADERS, API_URLS_WB
from api_requests import ApiError, read_json, send_request, wb_goods, wb_json
from utils import chunk_list


def get_fbs_quantity_ozon(offer_ids: list[str]) -> dict:
    """
    Получает остатки FBS по списку offer_id.
    Возвращает словарь:
    {
        offer_id: fbs_present,
        ...
    }
    """

    if not offer_ids:
        return {}
    result = {}

    cursor = ''
    seen = set()
    received = 0
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

        label = 'Ozon (остатки FBS)'
        response = send_request(
            'POST', API_URLS_OZON['product_info_stocks'], label=label,
            headers=OZON_HEADERS, json=payload, timeout=15,
        )
        data = read_json(response, label)
        items = data['items']
        if not isinstance(items, list):
            raise ApiError(f'{label}: некорректный список остатков.')

        received += len(items)
        total = data.get('total_items', data.get('total'))
        cursor = data.get('cursor', data.get('last_id', ''))
        if total is not None and total > received and (not cursor or not items):
            raise ApiError(f'{label}: пагинация завершилась до получения всех товаров.')

        for item in items:
            offer = item.get('offer_id')
            if not offer:
                continue

            stocks = item['stocks']

            for stock in stocks:
                s_type = stock.get('type', '').lower()
                if s_type == 'fbs':
                    result[offer] = stock['present']

        if not items:
            break
        if not isinstance(cursor, str) or cursor in seen:
            raise ApiError(f'{label}: некорректная или повторная страница.')
        if cursor:
            seen.add(cursor)
        if not cursor:
            break

    return result


def get_wb_fbs_warehouses() -> list[int]:
    """Возвращает ID складов продавца с типом доставки FBS."""
    warehouses = wb_json('GET', API_URLS_WB['warehouses'], 'warehouses', timeout=15)
    try:
        if not isinstance(warehouses, list):
            raise ValueError
        warehouse_ids = [warehouse['id'] for warehouse in warehouses if warehouse['deliveryType'] == 1]
        if any(type(item) is not int or item <= 0 for item in warehouse_ids):
            raise ValueError
        if len(set(warehouse_ids)) != len(warehouse_ids):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise ApiError('Wildberries (склады): некорректный список складов.') from None
    return warehouse_ids


def get_size_ids(*, stop_on_short_page: bool = False) -> dict[str, list[int]]:
    """Возвращает соответствие vendorCode и sizeID из полученных страниц каталога."""
    vendor_to_sizes = {}
    try:
        for item in wb_goods(stop_on_short_page=stop_on_short_page):
            vendor = item['vendorCode']
            sizes = item['sizes']
            if not isinstance(vendor, str) or not isinstance(sizes, list):
                raise ValueError
            size_ids = [size['sizeID'] for size in sizes]
            if any(type(size) is not int or size <= 0 for size in size_ids):
                raise ValueError
            if vendor:
                vendor_to_sizes.setdefault(vendor, []).extend(size_ids)
    except (KeyError, TypeError, ValueError):
        raise ApiError('Wildberries (товары): некорректные артикулы или размеры.') from None
    return vendor_to_sizes


def _read_wb_stock_batch(data, size_ids: list[int], warehouse_number: int, batch_number: int) -> dict[int, int]:
    context = f'Wildberries (FBS, склад №{warehouse_number}, пакет №{batch_number}): отправлено chrtIds={len(size_ids)}'
    stocks = data.get('stocks') if isinstance(data, dict) else None
    if not isinstance(stocks, list):
        raise ApiError(f'{context}, получено записей=н/д. В ответе отсутствует массив stocks.')

    context += f', получено записей={len(stocks)}'
    expected = set(size_ids)
    amounts = {}
    for stock in stocks:
        if not isinstance(stock, dict):
            raise ApiError(f'{context}. Запись остатка должна быть объектом.')
        size_id = stock.get('chrtId')
        amount = stock.get('amount')
        if type(size_id) is not int or size_id <= 0:
            raise ApiError(f'{context}. Отсутствует или некорректно поле chrtId.')
        if size_id not in expected:
            raise ApiError(f'{context}. В ответе есть незапрошенный chrtId.')
        if size_id in amounts:
            raise ApiError(f'{context}. В ответе повторяется chrtId.')
        if type(amount) is not int or amount < 0:
            raise ApiError(f'{context}. Поле amount должно содержать целое неотрицательное число.')
        amounts[size_id] = amount

    missing = len(expected) - len(amounts)
    if missing:
        raise ApiError(f'{context}. Неполный остаток: отсутствуют записи для {missing} запрошенных размеров.')
    return amounts


def get_fbs_quantity_wb(offer_ids: list[str], *, stop_on_short_page: bool = False) -> dict[str, int]:
    """Суммирует остатки каждого артикула по размерам и складам FBS."""
    if not offer_ids:
        return {}

    warehouses = get_wb_fbs_warehouses()
    if not warehouses:
        raise ApiError('Wildberries: склады FBS не найдены.')

    vendor_to_sizes = get_size_ids(stop_on_short_page=stop_on_short_page)
    result = dict.fromkeys(offer_ids, 0)
    vendor_map = {}
    missing = sum(not vendor_to_sizes.get(vendor) for vendor in result)
    if missing:
        raise ApiError(f'Wildberries: в каталоге отсутствуют размеры для {missing} артикулов Excel.')
    for vendor in result:
        for size_id in vendor_to_sizes[vendor]:
            if vendor_map.setdefault(size_id, vendor) != vendor:
                raise ApiError('Wildberries: один размер относится к разным артикулам.')

    for warehouse_number, warehouse_id in enumerate(warehouses, start=1):
        url = API_URLS_WB['stocks'].format(warehouseId=warehouse_id)
        for batch_number, chunk in enumerate(chunk_list(list(vendor_map), 1000), start=1):
            data = wb_json('POST', url, 'stocks', json={'chrtIds': chunk}, timeout=15)
            amounts = _read_wb_stock_batch(data, chunk, warehouse_number, batch_number)
            for size_id, amount in amounts.items():
                result[vendor_map[size_id]] += amount
    return result


def write_fbs_quantity_to_excel(fbs_data: dict, marketplace='ОЗОН', *, path=DATA_WORKBOOK) -> None:
    """
    Записывает остатки FBS в 16-й столбец Excel.
    Старт записи — с 4-й строки.
    """

    wb, ws = open_workbook_sheet(marketplace, path)

    for row in ws.iter_rows(min_row=4):
        offer_id = str(row[1].value).strip()
        if not offer_id:
            continue

        fbs_value = fbs_data.get(offer_id)
        if fbs_value is not None:
            ws.cell(row=row[1].row, column=16, value=fbs_value)

    save_workbook(wb, path)
    print('✅ Остатки FBS успешно записаны в Excel (16-й столбец)')


# Для ручного теста
if __name__ == '__main__':
    pass
