# utils.py

import requests

from configs.config import API_CREDENTIALS, API_URLS_WB


OZON_INVALID_TOKEN = (
    'API-токен Ozon недействителен или срок его действия истек.\n'
    'Для обновления токена выберите пункт 17.'
)
WB_INVALID_TOKEN = (
    'Ошибка авторизации Wildberries.\n'
    'API-токен отсутствует, недействителен или срок его действия истек.\n'
    'Для обновления токена выберите пункт 18.'
)
MISSING_TOKEN_MESSAGES = {
    'ozon': 'API-токен Ozon отсутствует. Для добавления выберите пункт 17.',
    'wb': WB_INVALID_TOKEN,
    'figma': 'API-токен Figma отсутствует. Запустите python -m configs.token_manager из папки проекта.',
}
API_NAMES = {'ozon': 'Ozon', 'wb': 'Wildberries', 'figma': 'Figma'}
AUTH_ERRORS = {
    ('ozon', 401): OZON_INVALID_TOKEN,
    ('ozon', 403): (
        'Ozon API отклонил доступ (HTTP 403). Проверьте токен и его права.\n'
        'Для обновления токена выберите пункт 17.'
    ),
    ('wb', 401): WB_INVALID_TOKEN,
    ('wb', 403): 'Доступ к Wildberries API запрещён (HTTP 403). Проверьте категорию и права токена.',
}


class ApiRequestError(requests.RequestException):
    """Ошибка API с сообщением без содержимого запроса или ответа."""


def check_token(service: str) -> bool:
    _, header, headers = API_CREDENTIALS[service]
    if headers.get(header, '').strip():
        return True
    print(MISSING_TOKEN_MESSAGES[service])
    return False


def request_api(service: str, send, url: str, *, headers: dict = None, **kwargs):
    _, token_header, configured_headers = API_CREDENTIALS[service]
    if headers is None:
        headers = configured_headers
    if not headers.get(token_header, '').strip():
        raise ApiRequestError(MISSING_TOKEN_MESSAGES[service])

    name = API_NAMES[service]
    try:
        response = send(url, headers=headers, allow_redirects=False, **kwargs)
    except requests.RequestException:
        raise ApiRequestError(f'{name} API недоступен: не удалось выполнить запрос.') from None

    status = response.status_code
    if not 200 <= status < 300:
        raise ApiRequestError(AUTH_ERRORS.get((service, status), f'{name} API: HTTP {status}.'))
    return response

# Словарь сервисов WB и их ping URL
WB_PING_URLS = {
    "common": API_URLS_WB['ping'],
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

    try:
        response = request_api('wb', requests.get, url, headers=headers, timeout=timeout)
        if response.json().get('Status') == 'OK':
            print(f"✅ Подключение к WB {service} API успешно")
            print('Status: OK')
            return True
        print(f"❌ WB {service} API вернул неожиданный статус")
    except ApiRequestError as e:
        print(f"❌ Ошибка подключения к WB {service} API: {e}")
    except (ValueError, AttributeError):
        print(f"❌ WB {service} API вернул некорректный ответ")
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
    for service_name in ("marketplace", "analytics", "prices"):
        check_wb_api_connection(service=service_name)
