import os
from datetime import datetime

import requests

import pandas as pd


def save_excel(data: list[dict], filename_prefix: str) -> None:
    """
    Сохраняет переданные данные в Excel-файл с текущей датой и временем в имени.
    """
    now_str = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"{filename_prefix}_{now_str}.xlsx"

    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f'✅ Данные сохранены в {filename}')


def save_csv(file_url: str, filename: str) -> None:
    """
    Сохраняет CSV по ссылке в указанный файл.

    :param file_url: URL CSV-файла от Ozon
    :param filename: Путь, куда сохранить файл
    """
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()

        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f'✅ CSV файл сохранён: {filename}')
    except requests.exceptions.RequestException as e:
        print(f'❌ Ошибка загрузки CSV: {e}')
    except IOError as e:
        print(f'❌ Ошибка сохранения CSV: {e}')
