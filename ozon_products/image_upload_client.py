# image_upload_client.py

from config import IMAGE_UPLOAD_SERVICE, YANDEX_OAUTH_TOKEN, YANDEX_DISK_BASE_DIR, IMGBB_API_KEY
from yandex_disk_client import YandexDiskClient
from imgbb_client import ImgbbClient

class ImageUploader:
    def __init__(self):
        if IMAGE_UPLOAD_SERVICE == 'yandex':
            self.client = YandexDiskClient(token=YANDEX_OAUTH_TOKEN, base_dir=YANDEX_DISK_BASE_DIR)
        elif IMAGE_UPLOAD_SERVICE == 'imgbb':
            self.client = ImgbbClient(api_key=IMGBB_API_KEY)
        else:
            raise ValueError(f'Неизвестный IMAGE_UPLOAD_SERVICE: {IMAGE_UPLOAD_SERVICE}')

    def upload(self, local_path: str) -> str | None:
        return self.client.upload(local_path)
