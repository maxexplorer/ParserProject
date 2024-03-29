import requests
import os
import json
from datetime import datetime

start_time = datetime.now()

# Установка заголовков HTTP
headers = {
    "Content-Type": "application/json"
}

session_token = 'CB8D65767A00CAFEE247A269090E27DADF900673E83C8D9291F3B03139BB4EE3'


def auth_requests():
    # Логин и пароль
    client_login = "100553"
    client_password = "BaUSEj"

    # Домен API
    api_url = "https://b2b.i-t-p.pro/api/2"

    # Составление JSON-RPC запроса для аутентификации
    data = {
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
    json_data = json.dumps(data)

    # Отправка POST запроса для аутентификации
    response = requests.post(api_url, data=json_data, headers=headers)

    # Проверка успешного статуса ответа аутентификации
    if response.status_code == 200 and response.json().get("success"):
        # Получение сессии из ответа
        session_token = response.json().get("session")
        return session_token
    else:
        # Вывести сообщение об ошибке аутентификации
        print(f"Ошибка аутентификации: {response.status_code}, Текст ответа: {response.text}")


def get_catalog(headers, session_token):
    # Составление JSON-RPC запроса с использованием сессии
    catalog_url = "https://b2b.i-t-p.pro/download/catalog/json/catalog_tree.json"

    data = {
        "data": {
            "session": session_token}
    }

    # Преобразование запроса в формат JSON
    json_data = json.dumps(data)

    try:
        # Отправка GET запроса для получения дерева категорий
        response = requests.get(catalog_url, data=json_data, headers=headers, timeout=60)

        # Запись ответа в файл формата JSON
        catalog_data = response.json()
        return catalog_data
    except Exception as ex:
        print(ex)


def get_list_products(headers, session_token):
    # Составление JSON-RPC запроса с использованием сессии
    product_url = "https://b2b.i-t-p.pro/download/catalog/json/products.json"

    data = {
        "data": {
            "session": session_token}
    }

    # Преобразование запроса в формат JSON
    json_data = json.dumps(data)

    try:
        # Отправка GET запроса для получения каталога продукции
        response = requests.get(product_url, data=json_data, headers=headers, timeout=60)

        products_data = response.json()
        return products_data
    except Exception as ex:
        print(ex)


def get_active_products_and_prices(headers, session_token):
    api_url = "https://b2b.i-t-p.pro/api/2"

    # Составление JSON-RPC запроса для получения наличия товаров и цен
    data = {
        "request": {
            "method": "get_active_products",
            "model": "client_api",
            "module": "platform"
        },
        "session": session_token
    }

    # Преобразование запроса в формат JSON
    json_data = json.dumps(data)

    try:
        # Отправка POST запроса для получения наличия товаров и цен
        response = requests.post(api_url, data=json_data, headers=headers, timeout=60)
        active_products_data = response.json()
        return active_products_data
    except Exception as ex:
        print(ex)

def get_adult_products_characteristics(headers, session_token):
    api_url = "https://b2b.i-t-p.pro/api/2"

    # Составление JSON-RPC запроса для получения наличия товаров и цен
    data = {
        "request": {
            "method": "get_adult_products_characteristics",
            "model": "client_api",
            "module": "platform"
        },
        "session": session_token
    }

    # Преобразование запроса в формат JSON
    json_data = json.dumps(data)

    try:
        # Отправка POST запроса для получения наличия товаров и цен
        response = requests.post(api_url, data=json_data, headers=headers, timeout=60)
        adult_products_data = response.json()
        return adult_products_data
    except Exception as ex:
        print(ex)

def save_json(data):
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_time}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def main():
    session_token = auth_requests()
    # catalog_data = get_catalog(headers=headers, session_token=session_token)
    # save_json(data=catalog_data)
    # products_data = get_list_products(headers=headers, session_token=session_token)
    # save_json(data=products_data)
    # active_products_data = get_active_products_and_prices(headers=headers, session_token=session_token)
    # save_json(data=active_products_data)
    adult_products_data = get_adult_products_characteristics(headers=headers, session_token=session_token)
    save_json(data=adult_products_data)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
