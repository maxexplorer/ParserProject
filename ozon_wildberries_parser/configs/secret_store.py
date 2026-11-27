import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path
from tempfile import NamedTemporaryFile

from app_paths import APP_DIR


SECRET_PATH = APP_DIR / 'configs' / '.api-secrets.dpapi'
CRYPTPROTECT_UI_FORBIDDEN = 0x01


class SecretStoreError(Exception):
    """Хранилище недоступно или содержит повреждённые данные."""


class _DataBlob(ctypes.Structure):
    _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.c_void_p)]


def _dpapi(data: bytes, *, protect: bool) -> bytes:
    crypt32 = ctypes.WinDLL('crypt32', use_last_error=True)
    local_free = ctypes.WinDLL('kernel32').LocalFree
    local_free.argtypes = [ctypes.c_void_p]
    local_free.restype = ctypes.c_void_p

    blob_pointer = ctypes.POINTER(_DataBlob)
    if protect:
        transform = crypt32.CryptProtectData
        description_type = wintypes.LPCWSTR
    else:
        transform = crypt32.CryptUnprotectData
        description_type = ctypes.POINTER(wintypes.LPWSTR)
    transform.argtypes = [blob_pointer, description_type, blob_pointer, ctypes.c_void_p,
                          ctypes.c_void_p, wintypes.DWORD, blob_pointer]
    transform.restype = wintypes.BOOL

    buffer = ctypes.create_string_buffer(data)
    source = _DataBlob(len(data), ctypes.addressof(buffer))
    destination = _DataBlob()
    try:
        if not transform(ctypes.byref(source), None, None, None, None,
                         CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(destination)):
            raise ctypes.WinError(ctypes.get_last_error())
        return ctypes.string_at(destination.pbData, destination.cbData)
    finally:
        ctypes.memset(buffer, 0, len(buffer))
        if destination.pbData:
            if not protect:
                ctypes.memset(destination.pbData, 0, destination.cbData)
            local_free(destination.pbData)


def _decode(ciphertext: bytes) -> dict[str, str]:
    try:
        secrets = json.loads(_dpapi(ciphertext, protect=False).decode('utf-8'))
    except (OSError, ValueError):
        raise SecretStoreError(
            'Не удалось расшифровать хранилище API-токенов. '
            'Войдите под исходным пользователем Windows или восстановите доступную копию файла.'
        ) from None
    if not isinstance(secrets, dict) or any(not isinstance(value, str) for value in secrets.values()):
        raise SecretStoreError('Неверный формат хранилища API-токенов.')
    return secrets


def load_secrets() -> dict[str, str]:
    try:
        ciphertext = SECRET_PATH.read_bytes()
    except FileNotFoundError:
        return {}
    except OSError:
        raise SecretStoreError('Не удалось прочитать хранилище API-токенов.') from None
    if os.name != 'nt':
        raise SecretStoreError('Для доступа к хранилищу API-токенов требуется Windows DPAPI.')
    return _decode(ciphertext)


def save_secrets(updates: dict[str, str]) -> dict[str, str]:
    """Объединяет изменения с сохранёнными секретами и возвращает результат."""
    if os.name != 'nt':
        raise SecretStoreError('Для сохранения API-токенов требуется Windows DPAPI.')

    import msvcrt

    # Отдельная блокировка сохраняет силу и после замены файла хранилища.
    lock_path = SECRET_PATH.with_suffix('.dpapi.lock')
    temp_path = None
    try:
        SECRET_PATH.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open('a+b') as lock:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            secrets = load_secrets()
            secrets.update(updates)
            ciphertext = _dpapi(json.dumps(secrets).encode('utf-8'), protect=True)
            with NamedTemporaryFile(mode='wb', dir=SECRET_PATH.parent, prefix=f'{SECRET_PATH.name}.',
                                    suffix='.tmp', delete=False) as temp:
                temp_path = Path(temp.name)
                temp.write(ciphertext)
                temp.flush()
                os.fsync(temp.fileno())
            if _decode(temp_path.read_bytes()) != secrets:
                raise SecretStoreError('Не удалось проверить записанные API-токены.')
            os.replace(temp_path, SECRET_PATH)
            temp_path = None
        return secrets
    except OSError:
        raise SecretStoreError('Не удалось сохранить хранилище API-токенов.') from None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
