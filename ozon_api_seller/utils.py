import os
from datetime import datetime

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
