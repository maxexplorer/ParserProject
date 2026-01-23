# yandex_disk.py

import os

import requests

YANDEX_UPLOAD_URL = 'https://cloud-api.yandex.net/v1/disk/resources/upload'


class YandexDiskClient:

    def __init__(self, token: str, base_dir: str):
        self.base_dir = base_dir.rstrip('/')
        self.headers = {
            'Authorization': f'OAuth {token}'
        }

    def upload(self, local_path: str, remote_name: str | None = None) -> str | None:
        if not remote_name:
            remote_name = os.path.basename(local_path)

        params = {
            'path': f'{self.base_dir}/{remote_name}',
            'overwrite': 'true'
        }

        r = requests.get(YANDEX_UPLOAD_URL, headers=self.headers, params=params)
        if r.status_code != 200:
            print(f'YD upload_url error: {r.text}')
            return None

        upload_url = r.json()['href']

        with open(local_path, 'rb') as f:
            r = requests.put(upload_url, files={'file': f})

        if r.status_code not in (201, 202):
            print(f'YD upload error: {r.text}')
            return None

        return f'{self.base_dir}/{remote_name}'
