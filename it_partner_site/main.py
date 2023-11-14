import requests
import json

# Аутентификация
auth_url = "https://b2b.i-t-p.pro/api/2"
auth_data = {
    "request": {
        "method": "login",
        "model": "auth",
        "module": "quickfox"
    },
    "data": {
        "login": "100553",
        "password": " BaUSEj"
    },
}

auth_headers = {
    'Content-Type': 'application/json'
}

response = requests.post(auth_url, data=json.dumps(auth_data), headers=auth_headers)
res_auth = response.json()

print(res_auth)

