"""Safe API errors and Wildberries request pacing."""

import base64
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

from configs.config import API_URLS_WB, WB_HEADERS


class ApiError(RuntimeError):
    """An operation could not obtain a complete, usable result."""


def send_request(method, url, *, label, headers, timeout=20, **kwargs):
    try:
        send = {'GET': requests.get, 'POST': requests.post}[method]
        return send(url, headers=headers, timeout=timeout, allow_redirects=False, **kwargs)
    except (requests.RequestException, ValueError):
        raise ApiError(f'{label}: ошибка соединения или запроса.') from None


def read_json(response, label, *, statuses=(200,)):
    if response.status_code not in statuses:
        raise ApiError(f'{label}: HTTP {response.status_code}.')
    try:
        return response.json()
    except ValueError:
        raise ApiError(f'{label}: некорректный JSON.') from None


def wb_token_claims(token: str) -> dict:
    """Read local JWT claims for pacing. WB validates the token itself."""
    if not isinstance(token, str):
        return {}
    try:
        _, payload, _ = token.removeprefix('Bearer ').split('.')
        padded = payload + '=' * (-len(payload) % 4)
        claims = json.loads(base64.b64decode(padded, altchars=b'-_', validate=True))
        return claims if isinstance(claims, dict) else {}
    except ValueError:
        return {}


def _retry_delay(headers):
    hints = []
    for name in ('X-Ratelimit-Retry', 'Retry-After'):
        value = headers.get(name)
        if value is None:
            continue
        try:
            delay = float(value)
        except ValueError:
            if name != 'Retry-After':
                continue
            try:
                retry_at = parsedate_to_datetime(value)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
            except (ValueError, TypeError, OverflowError):
                continue
        if math.isfinite(delay) and delay >= 0:
            hints.append(delay)
    if not hints:
        try:
            reset = float(headers.get('X-Ratelimit-Reset', '0'))
            if math.isfinite(reset) and reset >= 0:
                hints.append(reset)
        except ValueError:
            pass
    return max(hints, default=0)


_TOKEN_TYPES = {
    1: 'базовый токен',
    2: 'тестовый токен',
    3: 'персональный токен',
    4: 'сервисный токен',
}

# Regular and basic (without a service secret) intervals in seconds.
_INTERVALS = {
    'analytics': (20, 1800),
    'prices': (0.6, 900),
    'media': (0.6, 1800),
    'warehouses': (0.2, 0.2),
    'stocks': (0.2, 0.2),
    'ping': (10, 10),
}


@dataclass(frozen=True)
class _RequestDeadline:
    at: float
    reason: str
    after_429: bool = False


# Shared across menu actions. Prices methods share one bucket; each ping has its own.
_next_request: dict[tuple[str, bool], _RequestDeadline] = {}
_MAX_WAIT = 120
_ATTEMPTS = 4


def _show_wait(token_type: str, category: str, delay: float, reason: str) -> None:
    print(
        f'WB: {token_type}; категория {category}; '
        f'следующая попытка через {math.ceil(delay)} секунд. Причина — {reason}.',
        flush=True,
    )


def wb_json(method, url, category, *, headers=WB_HEADERS, statuses=(200,), retry=True, **kwargs):
    label = f'Wildberries ({category})'
    acc = wb_token_claims(headers.get('Authorization', '')).get('acc')
    acc = acc if type(acc) is int else None
    token_type = _TOKEN_TYPES.get(acc, 'токен неизвестного типа')
    basic = acc == 1
    interval = _INTERVALS[category][basic]
    bucket = (url if category == 'ping' else category, basic)
    interval_reason = f'интервал категории по лимиту токена ({interval:g} с)'
    for attempt in range(_ATTEMPTS if retry else 1):
        deadline = _next_request.get(bucket)
        delay = deadline.at - time.monotonic() if deadline else 0
        if delay > 0:
            _show_wait(token_type, category, delay, deadline.reason)
            if deadline.after_429 and delay > _MAX_WAIT:
                raise ApiError(f'{label}: HTTP 429, повторите не раньше чем через {math.ceil(delay)} сек.')
            time.sleep(delay)

        pace_until = time.monotonic() + interval
        _next_request[bucket] = _RequestDeadline(pace_until, interval_reason)
        response = send_request(method, url, label=label, headers=headers, **kwargs)
        if response.status_code != 429:
            return read_json(response, label, statuses=statuses)

        backoff = min(60, max(1, min(interval, 20)) * 2 ** attempt)
        server_delay = _retry_delay(response.headers)
        retry_at = time.monotonic() + max(backoff, server_delay)
        if pace_until > retry_at:
            deadline = _RequestDeadline(pace_until, f'HTTP 429 и {interval_reason}', after_429=True)
        else:
            reason = 'задержка по заголовкам WB' if server_delay >= backoff else 'экспоненциальная задержка'
            deadline = _RequestDeadline(retry_at, f'HTTP 429, {reason}', after_429=True)
        _next_request[bucket] = deadline
        if deadline.at - time.monotonic() > _MAX_WAIT:
            break

    delay = max(0, deadline.at - time.monotonic())
    _show_wait(token_type, category, delay, deadline.reason)
    raise ApiError(f'{label}: HTTP 429, повторите не раньше чем через {math.ceil(delay)} сек.')


def wb_goods(params=None):
    """Yield verified pages from the Prices and Discounts catalog."""
    limit = 1000
    offset = 0
    seen = set()
    while True:
        data = wb_json(
            'GET', API_URLS_WB['list_goods_filter'], 'prices',
            params={**(params or {}), 'limit': limit, 'offset': offset}, timeout=15,
        )
        try:
            goods = data['data']['listGoods']
            if data.get('error', False) or not isinstance(goods, list) or len(goods) > limit:
                raise ValueError
            ids = {item['nmID'] for item in goods}
            if any(type(item_id) is not int or item_id <= 0 for item_id in ids):
                raise ValueError
            if len(ids) != len(goods) or seen.intersection(ids):
                raise ValueError
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ApiError('Wildberries (товары): некорректная или повторная страница.') from None
        seen.update(ids)
        yield from goods
        if not goods:
            return
        offset += limit
