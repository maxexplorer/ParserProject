import re
import warnings
from datetime import datetime, timedelta, timezone
from getpass import GetPassWarning, getpass
from math import ceil

import requests

from configs import config
from configs.secret_store import SecretStoreError, load_secrets, save_secrets
from utils import API_NAMES, OZON_INVALID_TOKEN, ApiRequestError, check_token, request_api


def _get_ozon_expiration(headers: dict) -> datetime | None:
    response = request_api(
        'ozon', requests.post, config.API_URLS_OZON['roles'], headers=headers, json={}, timeout=5
    )
    try:
        data = response.json()
    except ValueError:
        raise ApiRequestError('Ozon API вернул некорректный ответ на запрос срока действия.') from None
    if not isinstance(data, dict):
        raise ApiRequestError('Ozon API вернул некорректный ответ на запрос срока действия.')

    value = data.get('expires_at')
    if not isinstance(value, str) or not value:
        return None
    # Python 3.10 принимает дробную часть секунды из трёх или шести цифр.
    value = re.sub(r'\.(\d+)', lambda match: '.' + match[1][:6].ljust(6, '0'), value, count=1)
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    try:
        expiration = datetime.fromisoformat(value)
    except ValueError:
        return None
    return expiration if expiration.tzinfo else expiration.replace(tzinfo=timezone.utc)


def _report_ozon_expiration(expiration: datetime | None) -> None:
    if expiration is None:
        print('Ozon: не удалось определить срок действия API-токена. Проверьте поле expires_at.')
        return
    remaining = expiration - datetime.now(timezone.utc)
    if remaining <= timedelta(0):
        print(OZON_INVALID_TOKEN)
        return

    days = ceil(remaining / timedelta(days=1))
    print('Ozon: API-токен активен.')
    print(f'Действителен до: {expiration.astimezone():%d.%m.%Y}.')
    print(f'Осталось дней: {days}.')
    if days <= config.OZON_EXPIRY_WARNING_DAYS:
        print('Внимание! Скоро истечёт срок действия API-токена Ozon.')
        print('Для обновления токена выберите пункт 17.')


def check_ozon_token_expiration() -> None:
    if config.SECRET_STORE_ERROR:
        print(config.SECRET_STORE_ERROR)
        return
    if not check_token('ozon'):
        return
    try:
        expiration = _get_ozon_expiration(config.OZON_HEADERS)
    except ApiRequestError as error:
        print(error)
        return
    _report_ozon_expiration(expiration)


def update_token(service: str) -> None:
    try:
        load_secrets()
    except SecretStoreError as error:
        print(error)
        return

    name = API_NAMES[service]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', GetPassWarning)
            token = getpass(f'Введите новый API-токен {name} (Enter без значения или Ctrl+C для отмены): ').strip()
    except (KeyboardInterrupt, EOFError):
        print('\nОбновление отменено.')
        return
    except (GetPassWarning, OSError):
        print('Скрытый ввод недоступен. Запустите программу в консоли Windows.')
        return
    if not token:
        print('Токен не введён. Обновление отменено.')
        return
    if any(not 33 <= ord(character) <= 126 for character in token):
        print('Токен содержит недопустимые символы.')
        return

    secret_name, header, headers = config.API_CREDENTIALS[service]
    candidate_headers = {**headers, header: token}
    expiration = None
    try:
        if service == 'ozon':
            expiration = _get_ozon_expiration(candidate_headers)
            if expiration is not None and expiration <= datetime.now(timezone.utc):
                print(OZON_INVALID_TOKEN)
                return
        elif service == 'wb':
            response = request_api(
                'wb', requests.get, config.API_URLS_WB['ping'], headers=candidate_headers, timeout=5
            )
            data = response.json()
            if not isinstance(data, dict) or data.get('Status') != 'OK':
                raise ApiRequestError('Wildberries API не подтвердил работу токена.')

        secrets = save_secrets({secret_name: token})
    except (ApiRequestError, SecretStoreError) as error:
        print(error)
        return
    except ValueError:
        print(f'{name} API вернул некорректный ответ при проверке токена.')
        return

    config.apply_api_secrets(secrets)
    config.SECRET_STORE_ERROR = None
    print(f'API-токен {name} успешно обновлён.')
    if service == 'ozon':
        _report_ozon_expiration(expiration)


if __name__ == '__main__':
    update_token('figma')
