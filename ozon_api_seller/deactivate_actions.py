import time

import requests
from configs.config import CLIENT_ID, API_KEY, API_URLS

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
}


def get_all_products(headers: dict) -> dict[int, str]:
    """
    Получает список всех товаров со статусом IN_SALE.

    :param headers: Заголовки для запроса с Client-Id и Api-Key
    :return: Список словарей {product_id: offer_id}
    """
    result_data = {}
    last_id = ''
    limit = 100
    total_printed = False

    while True:
        data = {
            'filter': {
                'visibility': 'IN_SALE'
            },
            'last_id': last_id,
            'limit': limit
        }

        try:
            time.sleep(1)  # пауза между запросами
            response = requests.post(
                API_URLS.get('product_list'),
                headers=headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'❌ Ошибка при запросе списка товаров: {e}')
            break

        try:
            data = response.json()
        except ValueError:
            print('❌ Невозможно декодировать JSON-ответ от сервера.')
            break

        result = data.get('result', {})
        items = result.get('items', [])
        total = result.get('total')

        if not total_printed:
            print(f'📦 Всего товаров: {total}')
            total_printed = True

        for item in items:
            offer_id = item.get('offer_id')
            product_id = item.get('product_id')
            if offer_id and product_id:
                result_data[product_id] = offer_id

        last_id = result.get('last_id', '')
        if not last_id:
            break

    return result_data


def get_all_actions(headers: dict) -> list:
    """
    Получает список всех доступных акций на аккаунте Ozon.

    :param headers: Заголовки запроса
    :return: Список ID акций или пустой список.
    """

    try:
        response = requests.get(API_URLS.get('actions'), headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'❌ Ошибка при запросе списка акций: {e}')
        return []

    try:
        data = response.json()
    except ValueError:
        print('❌ Ошибка при декодировании JSON-ответа.')
        return []

    actions = data.get('result', [])
    print(f'📊 Найдено акций: {len(actions)}')

    action_ids = []
    for action in actions:
        action_id = action.get('id')
        if action_id:
            action_ids.append(action_id)

    return action_ids


def get_action_products(headers: dict, action_ids: list) -> dict[int, list[int]]:
    """
    Получить все товары, участвующие в каждой акции по списку action_id.

    :param headers: Заголовки с авторизацией
    :param action_ids: Список ID акций
    :return: Словарь {action_id: [список id товаров]}
    """
    result_data = {}
    limit = 100

    for action_id in action_ids:
        print(f'🔍 Обработка акции ID {action_id}...')
        last_id = ''

        while True:
            data = {
                'action_id': action_id,
                'limit': limit,
                'offset': 0,
                'last_id': last_id
            }

            try:
                time.sleep(1)
                response = requests.post(
                    API_URLS.get('action_products'),
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка при получении товаров акции {action_id}: {e}")
                break

            try:
                data = response.json()
            except ValueError:
                print(f'❌ Ошибка при декодировании JSON для акции {action_id}.')
                break

            result = data.get('result', {})
            products = result.get('products', [])

            for product in products:
                product_id = product.get('id')
                mode = product.get('add_mode')
                if mode == 'AUTO':
                    result_data.setdefault(action_id, []).append(product_id)

            print(f'✅ Обработано товаров: {len(products)}')

            last_id = result.get('last_id', '')
            if not products or not last_id:
                break

    return result_data


def deactivate_action_products(headers: dict, action_products: dict[int, list[int]]) -> None:
    """
    Удаляет товары из указанных акций.

    :param headers: Заголовки с авторизацией
    :param action_products: Словарь вида {action_id: [product_id1, product_id2, ...]}
    """
    for action_id, product_ids in action_products.items():
        print(f'⛔ Удаление товаров из акции ID {action_id}...')

        data = {
            'action_id': action_id,
            'product_ids': product_ids
        }

        try:
            time.sleep(1)  # пауза для избежания лимитов
            response = requests.post(
                API_URLS.get('action_products_deactivate'),
                headers=headers,
                json=data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'❌ Ошибка при удалении товаров из акции {action_id}: {e}')
            continue

        try:
            data = response.json()
        except ValueError:
            print(f'❌ Ошибка декодирования JSON для акции {action_id}.')
            continue

        result = data.get('result', {})
        removed = result.get('product_ids', [])
        rejected = result.get('rejected', [])

        print(f'✅ Удалено: {len(removed)} товаров.')
        if rejected:
            print(f'⚠️ Не удалось удалить: {rejected}')


def run_deactivate_actions():
    action_ids = get_all_actions(headers=headers)
    action_products = get_action_products(headers=headers, action_ids=action_ids)
    deactivate_action_products(headers=headers, action_products=action_products)
