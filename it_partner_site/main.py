import requests
import json

# Замените эти значения на свои реальные логин и пароль
client_login = "100553"
client_password = "BaUSEj"

# Замените на реальный домен вашего API
api_url = "https://b2b.i-t-p.pro/api/2"

# Составление JSON-RPC запроса для аутентификации
auth_request = {
    "data": {
        "login": client_login,
        "password": client_password
    },
    "request": {
        "method": "login",
        "model": "auth",
        "module": "quickfox"
    }
}

# Преобразование запроса в формат JSON
auth_json_data = json.dumps(auth_request)

# Установка заголовков HTTP
headers = {
    "Content-Type": "application/json"
}

# Отправка POST запроса для аутентификации
auth_response = requests.post(api_url, data=auth_json_data, headers=headers)

# Проверка успешного статуса ответа аутентификации
if auth_response.status_code == 200 and auth_response.json().get("success"):
    # Получение сессии из ответа
    session_token = auth_response.json().get("session")

    # Составление JSON-RPC запроса с использованием сессии
    api_request_with_session = {
        "data": {
            # Добавляем сессию к данным запроса
            "session": session_token,
            # Другие данные запроса...
        },
        "request": {
            "method": "your_method",
            "model": "your_model",
            "module": "your_module"
        }
    }

    # Преобразование запроса в формат JSON
    api_json_data_with_session = json.dumps(api_request_with_session)

    # Отправка POST запроса с использованием сессии
    api_response = requests.post(api_url, data=api_json_data_with_session, headers=headers)

    # Печать ответа
    print(api_response.json())
else:
    # Вывести сообщение об ошибке аутентификации
    print(f"Ошибка аутентификации: {auth_response.status_code}, Текст ответа: {auth_response.text}")
