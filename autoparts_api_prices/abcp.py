import requests


def search_article(url, login, password, number, brand):

    params = {
        "userlogin": login,
        "userpsw": password,
        "number": number,
        "brand": brand,
        "useOnlineStocks": 1,
        "disableFiltering": 1
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()