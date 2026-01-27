# yandex_disk_client.py

import os
import requests

from config import YANDEX_UPLOAD_URL, YANDEX_PUBLISH_URL, YANDEX_RESOURCES_URL

class YandexDiskClient:

    def __init__(self, token: str, base_dir: str):
        self.base_dir = base_dir.rstrip('/')
        self.headers = {'Authorization': f'OAuth {token}'}

    def upload(self, local_path: str, remote_name: str | None = None) -> str | None:
        if not remote_name:
            remote_name = os.path.basename(local_path)

        yandex_path = f'{self.base_dir}/{remote_name}'

        # 1️⃣ Получаем URL для загрузки
        r = requests.get(YANDEX_UPLOAD_URL, headers=self.headers, params={'path': yandex_path, 'overwrite': 'true'})
        if r.status_code != 200:
            print(f'YD upload_url error: {r.text}')
            return None
        upload_url = r.json().get('href')
        if not upload_url:
            print(f'YD upload_url missing href: {r.text}')
            return None

        # 2️⃣ Загружаем файл на диск
        with open(local_path, 'rb') as f:
            r = requests.put(upload_url, files={'file': f})
        if r.status_code not in (201, 202):
            print(f'YD upload error: {r.text}')
            return None

        # 3️⃣ Публикуем файл
        r = requests.put(YANDEX_PUBLISH_URL, headers=self.headers, params={'path': yandex_path})
        if r.status_code != 200:
            print(f'YD publish error: {r.text}')
            return None

        # 4️⃣ Получаем метаинформацию о файле, чтобы взять public_url
        r = requests.get(YANDEX_RESOURCES_URL, headers=self.headers, params={'path': yandex_path})
        if r.status_code != 200:
            print(f'YD resource info error: {r.text}')
            return None

        file_info = r.json()

        download_url = file_info.get('file')
        if not download_url:
            print(f'YD public_url missing in response: {r.json()}')
            return None

        return download_url

