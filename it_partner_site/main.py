# import requests
# import json
#
# # Аутентификация
# auth_url = "https://b2b.i-t-p.pro/api/2"
# auth_data = {
#     "request": {
#         "method": "login",
#         "model": "auth",
#         "module": "quickfox"
#     },
#     "data": {
#         "login": "100553",
#         "password": "BaUSEj"
#     },
# }
#
# auth_headers = {
#     'Content-Type': 'application/json'
# }
#
# response = requests.post(auth_url, data=json.dumps(auth_data), headers=auth_headers)
# res_auth = response.json()
#
# print(res_auth)


import requests
import json

# Замените эти значения на свои реальные логин и пароль
client_login = "100553"
client_password = "BaUSEj"

# Замените на реальный домен вашего API
api_url = "https://b2b.i-t-p.pro/api/2"

# Составление JSON-RPC запроса
json_rpc_request = {
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
json_data = json.dumps(json_rpc_request)

# Установка заголовков HTTP
headers = {
    "Content-Type": "application/json"
}

# Отправка POST запроса
response = requests.post(api_url, data=json_data, headers=headers)

# Печать ответа
print(response.json())

