import requests
import os
import json

# Установка заголовков HTTP
headers = {
    "Content-Type": "application/json"
}

session_token = '87B55ABD905374551FF06467D112EB5DA5FD70E14EA1E373E161B3CE10C0AE4E'

def auth_requests():
    # Логин и пароль
    client_login = "100553"
    client_password = "BaUSEj"

    # Домен API
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

    # Отправка POST запроса для аутентификации
    auth_response = requests.post(api_url, data=auth_json_data, headers=headers)

    # Проверка успешного статуса ответа аутентификации
    if auth_response.status_code == 200 and auth_response.json().get("success"):
        # Получение сессии из ответа
        session_token = auth_response.json().get("session")
        return session_token
    else:
        # Вывести сообщение об ошибке аутентификации
        print(f"Ошибка аутентификации: {auth_response.status_code}, Текст ответа: {auth_response.text}")

    session_token = '87B55ABD905374551FF06467D112EB5DA5FD70E14EA1E373E161B3CE10C0AE4E'


def get_tree_catalog(headers, session_token):
    # Составление JSON-RPC запроса с использованием сессии
    catalog_url = "https://b2b.i-t-p.pro/download/catalog/json/catalog_tree.json"

    api_request_with_session = {
        "data": {
            "session": session_token}
    }

    # Преобразование запроса в формат JSON
    api_json_data_with_session = json.dumps(api_request_with_session)

    # Отправка POST запроса с использованием сессии
    api_response = requests.get(catalog_url, data=api_json_data_with_session, headers=headers)

    # Запись ответа в файл формата JSON
    data = api_response.json()
    return data


def save_json(data):
    print(data)
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def main():
    data = get_tree_catalog(headers=headers, session_token=session_token)
    save_json(data=data)


if __name__ == '__main__':
    main()
