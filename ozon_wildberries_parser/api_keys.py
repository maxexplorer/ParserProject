"""Validate candidate credentials before replacing the active ones."""

import warnings
from datetime import datetime, timedelta, timezone
from getpass import GetPassWarning, getpass

from api_requests import ApiError, read_json, send_request, wb_json, wb_token_claims
from configs import config
from configs.secret_store import save_secrets
from utils import WB_PING_URLS


def _ozon_expiry(headers, *, timeout=10):
    label = 'Ozon (проверка ключа)'
    response = send_request(
        'POST', config.API_URLS_OZON['roles'], label=label, headers=headers, json={}, timeout=timeout
    )
    data = read_json(response, label)
    try:
        if not isinstance(data['roles'], list):
            raise ValueError
        value = data.get('expires_at')
        if not value:
            return None
        expires = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if expires.tzinfo is None:
            raise ValueError
        return expires
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ApiError(f'{label}: некорректный ответ.') from None


def _warn_expiry(expires):
    if expires is None:
        return
    remaining = expires - datetime.now(timezone.utc)
    if remaining <= timedelta(0):
        print('⚠️ Срок действия ключа Ozon истёк. Обновите ключ через пункт 17.')
    elif remaining <= timedelta(days=14):
        print(f'⚠️ Ключ Ozon действует до {expires.astimezone():%d.%m.%Y %H:%M}. Обновите его через пункт 17.')


def check_ozon_key_expiry():
    if not config.OZON_HEADERS.get('Api-Key'):
        return
    try:
        _warn_expiry(_ozon_expiry(config.OZON_HEADERS, timeout=5))
    except ApiError as error:
        print(f'⚠️ Не удалось проверить срок действия ключа. {error}')


def _validate_wb(headers):
    claims = wb_token_claims(headers['Authorization'])
    scope = claims.get('s')
    if type(scope) is int and scope & (1 << 30):
        raise ApiError('Wildberries: для обновления цен и изображений нужен токен с правом записи.')
    for category in ('analytics', 'prices', 'marketplace', 'content'):
        data = wb_json('GET', WB_PING_URLS[category], 'ping', headers=headers, timeout=5)
        if not isinstance(data, dict) or data.get('Status') != 'OK':
            raise ApiError(f'Wildberries ({category}): некорректный ответ проверки.')


def update_api_key(marketplace):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', GetPassWarning)
            candidate = getpass(f'Введите новый API-ключ {marketplace} (Enter для отмены): ').strip()
    except (GetPassWarning, EOFError):
        raise ApiError('Скрытый ввод недоступен. Запустите программу в обычном терминале.') from None
    except KeyboardInterrupt:
        print('Замена ключа отменена.')
        return

    if not candidate:
        print('Замена ключа отменена.')
        return
    if not candidate.isascii() or any(not 33 <= ord(char) <= 126 for char in candidate):
        raise ApiError('Недопустимые символы в API-ключе.')

    expires = None
    if marketplace == 'Ozon':
        headers, header, field = config.OZON_HEADERS, 'Api-Key', 'ozon_key'
        expires = _ozon_expiry({**headers, header: candidate})
        if expires is not None and expires <= datetime.now(timezone.utc):
            raise ApiError('Срок действия нового ключа Ozon истёк.')
    else:
        headers, header, field = config.WB_HEADERS, 'Authorization', 'wb_key'
        _validate_wb({**headers, header: candidate})

    secrets = {**config.SECRETS, field: candidate}
    try:
        save_secrets(secrets)
    except (OSError, ValueError):
        raise ApiError('Не удалось сохранить ключ в защищённом хранилище Windows.') from None

    config.SECRETS.update(secrets)
    # Imported headers are shared references. Keep their identity on rotation.
    headers[header] = candidate
    print(f'✅ API-ключ {marketplace} обновлён.')
    _warn_expiry(expires)
