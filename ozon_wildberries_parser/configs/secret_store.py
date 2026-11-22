"""Local credentials encrypted with Windows DPAPI for the current user."""

import ctypes
import json
import os
import tempfile
from ctypes import wintypes
from pathlib import Path


SECRET_PATH = Path(__file__).with_name('.api-secrets.dpapi')


class DataBlob(ctypes.Structure):
    _fields_ = [('size', wintypes.DWORD), ('data', ctypes.c_void_p)]


def _dpapi(data: bytes, *, encrypt: bool) -> bytes:
    if os.name != 'nt':
        raise OSError('Windows DPAPI is required for local credentials')
    buffer = ctypes.create_string_buffer(data)
    source = DataBlob(len(data), ctypes.addressof(buffer))
    target = DataBlob()
    crypt = ctypes.windll.crypt32
    function = crypt.CryptProtectData if encrypt else crypt.CryptUnprotectData
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        ctypes.windll.kernel32.LocalFree(ctypes.c_void_p(target.data))


def load_secrets() -> dict:
    try:
        encrypted = SECRET_PATH.read_bytes()
    except FileNotFoundError:
        return {}
    return json.loads(_dpapi(encrypted, encrypt=False))


def save_secrets(secrets: dict) -> None:
    encrypted = _dpapi(json.dumps(secrets).encode('utf-8'), encrypt=True)
    output = tempfile.NamedTemporaryFile(
        dir=SECRET_PATH.parent, prefix='.api-secrets-', suffix='.tmp', delete=False
    )
    temporary = Path(output.name)
    try:
        with output:
            output.write(encrypted)
        os.replace(temporary, SECRET_PATH)
    finally:
        temporary.unlink(missing_ok=True)
