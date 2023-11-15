import requests
import json

# # Замените эти значения на свои реальные логин и пароль
# client_login = "100553"
# client_password = "BaUSEj"
#
# # Замените на реальный домен вашего API
# api_url = "https://b2b.i-t-p.pro/api/2"
#
# # Составление JSON-RPC запроса для аутентификации
# auth_request = {
#     "data": {
#         "login": client_login,
#         "password": client_password
#     },
#     "request": {
#         "method": "login",
#         "model": "auth",
#         "module": "quickfox"
#     }
# }
#
# # Преобразование запроса в формат JSON
# auth_json_data = json.dumps(auth_request)
#
# Установка заголовков HTTP
headers = {
    "Content-Type": "application/json"
}
#
# # Отправка POST запроса для аутентификации
# auth_response = requests.post(api_url, data=auth_json_data, headers=headers)
#
# print(auth_response.json())

# # Проверка успешного статуса ответа аутентификации
# if auth_response.status_code == 200 and auth_response.json().get("success"):
#     # Получение сессии из ответа
session_token = '87B55ABD905374551FF06467D112EB5DA5FD70E14EA1E373E161B3CE10C0AE4E'

# Составление JSON-RPC запроса с использованием сессии

catalog_url = "https://b2b.i-t-p.pro/download/catalog/json/catalog_tree.json"

api_request_with_session = {
    "data": {
        "session": session_token}
}

# Преобразование запроса в формат JSON
api_json_data_with_session = json.dumps(api_request_with_session)

# Отправка POST запроса с использованием сессии
api_response = requests.post(catalog_url, data=api_json_data_with_session, headers=headers)

# Печать ответа
print(api_response.json())

