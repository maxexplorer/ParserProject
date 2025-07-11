import requests

from configs.config import WB_HEADERS

def check_wb_api_connection(timeout: int = 5) -> bool:
    url = "https://common-api.wildberries.ru/ping"
    try:
        response = requests.get(url, headers=WB_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return True
        else:
            print(f"Ошибка подключения: статус {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Ошибка подключения к Wildberries API: {e}")
        return False


if check_wb_api_connection():
    print("Подключение к Wildberries API успешно")
else:
    print("Не удалось подключиться к Wildberries API")
