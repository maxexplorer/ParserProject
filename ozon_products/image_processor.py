# image_processor.py

import os
import re

from io import BytesIO
from urllib.parse import urlparse

from PIL import Image
from requests import Session


processed_images_cache: dict[str, str] = {}


def crop_image(img: Image.Image, side: str, pixels: int) -> Image.Image:
    width, height = img.size

    if pixels <= 0:
        return img

    if side == 'top':
        return img.crop((0, pixels, width, height))
    if side == 'bottom':
        return img.crop((0, 0, width, height - pixels))
    if side == 'left':
        return img.crop((pixels, 0, width, height))
    if side == 'right':
        return img.crop((0, 0, width - pixels, height))

    raise ValueError(f'Unknown crop side: {side}')


def process_image(
    image_url: str,
    session: Session,
    save_dir: str,
    crop: dict | None = None,
    quality: int = None,
) -> str | None:

    if image_url in processed_images_cache:
        return processed_images_cache[image_url]

    try:
        url_path = urlparse(image_url).path
        filename = os.path.basename(url_path)
        filename = re.sub(r'[^\w\-.]', '_', filename)

        local_path = os.path.join(save_dir, filename)

        response = session.get(image_url, timeout=30)
        if response.status_code != 200:
            print(f'Image download error: {image_url}')
            return None

        img = Image.open(BytesIO(response.content)).convert('RGB')

        if crop:
            img = crop_image(
                img,
                side=crop['side'],
                pixels=crop['pixels']
            )

        img.save(local_path, format='JPEG', quality=quality)

        processed_images_cache[image_url] = local_path
        return local_path

    except Exception as ex:
        print(f'process_image error: {ex}')
        return None
