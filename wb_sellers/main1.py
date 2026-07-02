import os
import random
import time
from datetime import datetime

import requests
from pandas import DataFrame, ExcelWriter, read_excel


start_time = datetime.now()
SELLER_PAUSE_SECONDS = (4, 8)
INNER_REQUEST_PAUSE_SECONDS = (1, 3)

cookies = {
    '_wbauid': '7163656111752145777',
    'external-locale': 'ru',
    '_ga': 'GA1.1.1098996660.1758261326',
    '_ga_TXRZMJQDFE': 'GS2.1.s1759146135$o7$g0$t1759146135$j60$l0$h0',
    '_cp': '1',
    '__zzatw-wb': 'MDA0dBA=Fz2+aQ==',
    'cfidsw-wb': '/Cb1YoYAOLI/SCEhfiZq8bnsN+vkHtARk4gqgA18RS6OXNFdyhYUxbJ4hZrUcizLbBeETTj0/ZNVni2V+7QENlraGmsmO1zjyyprzCY8z9eb+NqimrZ2P+RKbDzDFrw5EOPOcl037573sXLDBCbz8vyJxMSTii0QuDR/',
    'routeb': '1779107226.277.2237.497709|fc3b37d75a18d923fd0e9c7589719997',
    'device_id': '2fabf07d-d2d6-4030-a541-d7db3985e3d1',
    'tours-city-id': '274286',
    'x_wbaas_token': '1.1000.cda4ebf4f79247e5a29ecd3b015915a7.MHw0NS4xMjkuMTQxLjE5NXxNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTQ5LjAuMC4wIFNhZmFyaS81MzcuMzZ8MTc4MzA4NTQyM3xyZXVzYWJsZXwyfGV5Sm9ZWE5vSWpvaUluMD18MXwzfDE3ODI5NTU4MjN8MQ==.MEYCIQCJgUm4XWZDnGDG/efbAyqNv9puSCTImPD5NalXi69IGwIhAL4gqaJ4duV8d0VOWNFQeJP7/tqltDnNP33o7Vf04bv5',
}

seller_page_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
}


def get_api_headers(seller_id: int) -> dict:
    return {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.wildberries.ru',
        'priority': 'u=1, i',
        'referer': f'https://www.wildberries.ru/seller/{seller_id}',
        'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': seller_page_headers['user-agent'],
        'x-client-name': 'site',
    }


def get_catalog_headers(seller_id: int) -> dict:
    headers = get_api_headers(seller_id)
    headers.update({
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '14.15.2',
    })
    return headers


def sleep_if_429(response: requests.Response) -> bool:
    if response.status_code != 429:
        return False

    retry_after = response.headers.get('Retry-After')
    try:
        pause = int(retry_after) if retry_after else 5
    except ValueError:
        pause = 5

    print(f'429. Пауза {pause} секунд')
    time.sleep(pause)
    return True


def random_pause(seconds_range: tuple[int, int]) -> None:
    pause = random.uniform(*seconds_range)
    time.sleep(pause)


def get_seller_page(seller_id: int) -> requests.Response | None:
    url = f'https://www.wildberries.ru/seller/{seller_id}'

    for _ in range(3):
        try:
            response = requests.get(
                url,
                cookies=cookies,
                headers=seller_page_headers,
                timeout=(5, 20),
            )
        except Exception as ex:
            print(f'Продавец {seller_id}: ошибка страницы продавца: {ex}')
            time.sleep(10)
            continue

        if sleep_if_429(response):
            continue

        return response

    return None


def seller_has_products(seller_id: int) -> bool:
    params = {
        'appType': '1',
        'curr': 'rub',
        'dest': '123585494',
        'sort': 'popular',
        'spp': '30',
        'supplier': seller_id,
    }

    for _ in range(3):
        try:
            response = requests.get(
                'https://catalog.wb.ru/sellers/v4/catalog',
                params=params,
                cookies=cookies,
                headers=get_catalog_headers(seller_id),
                timeout=(5, 20),
            )
        except Exception as ex:
            print(f'Продавец {seller_id}: ошибка каталога: {ex}')
            time.sleep(10)
            continue

        if sleep_if_429(response):
            continue

        if response.status_code != 200:
            print(f'Продавец {seller_id}: статус каталога {response.status_code}')
            return False

        try:
            products = response.json().get('products', [])
        except ValueError:
            return False

        return bool(products)

    return False


def get_inn(seller_id: int) -> str | None:
    try:
        response = requests.get(
            f'https://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/{seller_id}.json',
            cookies=cookies,
            headers=get_api_headers(seller_id),
            timeout=(5, 20),
        )

        if response.status_code != 200:
            print(f'Продавец {seller_id}: статус ИНН {response.status_code}')
            return None

        return response.json().get('inn')
    except Exception as ex:
        print(f'Ошибка при получении ИНН для {seller_id}: {ex}')
        return None


def get_registration_date_and_inn(seller_id: int) -> dict | None:
    try:
        response = requests.get(
            f'https://suppliers-shipment-2.wildberries.ru/api/v1/suppliers/{seller_id}',
            cookies=cookies,
            headers=get_api_headers(seller_id),
            timeout=(5, 20),
        )

        if response.status_code != 200:
            print(f'Продавец {seller_id}: статус статистики {response.status_code}')
            return None

        json_data = response.json()
    except Exception as ex:
        print(f'Ошибка при получении данных о регистрации для {seller_id}: {ex}')
        return None

    registration_date = json_data.get('registrationDate')
    sale_item_quantity = json_data.get('saleItemQuantity')

    if not registration_date or sale_item_quantity is None:
        return None

    reg_date = datetime.strptime(registration_date, '%Y-%m-%dT%H:%M:%SZ')
    years_on_wb = (datetime.now() - reg_date).days // 365

    if (
            (years_on_wb == 1 and sale_item_quantity >= 1000) or
            (years_on_wb == 2 and sale_item_quantity >= 4001) or
            (years_on_wb >= 3 and sale_item_quantity >= 9001)
    ):
        return {
            'Ссылка': f'https://www.wildberries.ru/seller/{seller_id}',
            'ИНН': get_inn(seller_id),
        }

    return None


def process_sellers_range(start_id: int, end_id: int, batch_size: int = 50) -> None:
    result_list = []

    for seller_id in range(start_id, end_id + 1):
        response = get_seller_page(seller_id)

        if response is None:
            print(f'Продавец {seller_id}: страница не получена')
            continue

        if response.status_code == 404:
            print(f'Продавец {seller_id}: страница 404')
            continue

        if response.status_code != 200:
            print(f'Продавец {seller_id}: статус страницы {response.status_code}')
            continue

        random_pause(INNER_REQUEST_PAUSE_SECONDS)

        if not seller_has_products(seller_id):
            print(f'Продавец {seller_id}: нет товаров')
            continue

        result = get_registration_date_and_inn(seller_id)

        if result is None:
            print(f'Обработан продавец ID: {seller_id}')
            continue

        result_list.append(result)
        print(f'Обработан продавец ID: {seller_id}, inn: {result["ИНН"]}')

        if len(result_list) >= batch_size:
            save_excel(result_list)
            result_list.clear()

        random_pause(SELLER_PAUSE_SECONDS)

    if result_list:
        save_excel(result_list)


def save_excel(data: list[dict]) -> None:
    directory = 'results'
    file_path = f'{directory}/result_data.xlsx'

    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Sellers', index=False)

    df_existing = read_excel(file_path, sheet_name='Sellers')
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows + 1,
            header=(num_existing_rows == 0),
            sheet_name='Sellers',
            index=False,
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def main() -> None:
    start_id = 4_000_000
    end_id = 5_000_000

    process_sellers_range(start_id, end_id)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен.')
    print(f'Время выполнения: {execution_time}')


if __name__ == '__main__':
    main()
