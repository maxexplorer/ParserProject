# imgbb_client.py
import os
import requests

class ImgbbClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.uploaded_files = {}  # кэш загруженных файлов, чтобы не загружать повторно

    def upload(self, local_path: str) -> str | None:
        filename = os.path.basename(local_path)

        # Если уже загружали, возвращаем URL из кэша
        if filename in self.uploaded_files:
            return self.uploaded_files[filename]

        try:
            with open(local_path, 'rb') as f:
                payload = {'key': self.api_key}
                files = {'image': f}
                response = self.session.post(
                    "https://api.imgbb.com/1/upload",
                    data=payload, files=files, timeout=60
                )

            result = response.json()
            if response.status_code == 200 and result.get('success'):
                url = result['data']['url']
                self.uploaded_files[filename] = url
                return url
            else:
                print(f'Ошибка загрузки на imgbb: {result}')
                return None
        except Exception as e:
            print(f'Ошибка загрузки файла {filename} на imgbb: {e}')
            return None
