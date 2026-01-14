# utils.py

import requests

from configs.config import WB_ANALYTICS_TOKEN, WB_MARKETPLACE_TOKEN, WB_PRICES_AND_DISCOUNTS_TOKEN

# Словарь сервисов WB и их ping URL
WB_PING_URLS = {
    "common": "https://common-api.wildberries.ru/ping",
    "marketplace": "https://marketplace-api.wildberries.ru/ping",
    "analytics": "https://seller-analytics-api.wildberries.ru/ping",
    "prices": "https://discounts-prices-api.wildberries.ru/ping",
    "statistics": "https://statistics-api.wildberries.ru/ping",
    "content": "https://content-api.wildberries.ru/ping",
    "advert": "https://advert-api.wildberries.ru/ping",
    "feedbacks": "https://feedbacks-api.wildberries.ru/ping",
    "buyer_chat": "https://buyer-chat-api.wildberries.ru/ping",
    "supplies": "https://supplies-api.wildberries.ru/ping",
    "returns": "https://returns-api.wildberries.ru/ping",
    "documents": "https://documents-api.wildberries.ru/ping",
    "finance": "https://finance-api.wildberries.ru/ping",
    "user_management": "https://user-management-api.wildberries.ru/ping",
}


def check_wb_api_connection(service: str = "common", headers: dict = None, timeout: int = 5) -> bool:
    """
    Проверяет подключение к Wildberries API и валидность токена.
    service: ключ сервиса WB из WB_PING_URLS
    headers: словарь с токеном Authorization
    """
    url = WB_PING_URLS.get(service)
    if not url:
        print(f"❌ Сервис '{service}' не найден в списке WB_PING_URLS")
        return False

    if headers is None:
        headers = {}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Подключение к WB {service} API успешно")
            status = response.json()["Status"]
            print(f'Status: {status}')
            return True
        elif response.status_code == 401:
            print(f"❌ Неверный токен для сервиса '{service}'")
            return False
        else:
            print(f"❌ Ошибка подключения к WB {service} API: статус {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Ошибка подключения к WB {service} API: {e}")
        return False


def chunk_list(data: list, chunk_size: int):
    """
    Разбивает список на чанки фиксированного размера.
    """
    if chunk_size <= 0:
        raise ValueError('chunk_size должен быть больше 0')

    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def make_wb_headers(token: str, use_bearer: bool = False) -> dict:
    """
    Возвращает словарь заголовков для Wildberries API.
    :param token: токен WB
    :param use_bearer: добавлять ли префикс 'Bearer' (для аналитики)
    """
    auth_value = f'Bearer {token}' if use_bearer else token
    return {
        'Authorization': auth_value,
        'Content-Type': 'application/json'
    }


if __name__ == "__main__":
    # Проверка токенов для разных сервисов
    services = {
        "marketplace": {"headers": {"Authorization": WB_MARKETPLACE_TOKEN}},
        "analytics": {"headers": {"Authorization": WB_ANALYTICS_TOKEN}},
        "prices": {"headers": {"Authorization": WB_PRICES_AND_DISCOUNTS_TOKEN}},
    }

    for service_name, params in services.items():
        check_wb_api_connection(service=service_name, headers=params["headers"])
