import requests
import os
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup

url = "https://www.dns-shop.ru"
url_api = "https://restapi.dns-shop.ru/v1/get-menu-header?shortMenu=1"
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

def get_html(url: str, headers: dict, session: requests.sessions.Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)

def get_json(url: str, headers: dict, session: requests.sessions.Session) -> dict:
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        print(response.status_code)
        json = response.json()
        return json
    except Exception as ex:
        print(ex)


def get_products(search: str) -> list:
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }
    url = f'https://www.dns-shop.ru/search/?q={search}&p=1&order=popular&stock=all'
    session = requests.session()
    session.headers.update(headers)

    rs = session.get(url)
    print(rs.status_code)
    data = json.loads(rs.text)


    root = BeautifulSoup(data['html'], 'html.parser')

    items = []

    for a in root.select('.product-info__title-link > a'):
        items.append(
            (a.get_text(strip=True), urljoin(rs.url, a['href']))
        )
    return items




def get_data(url: str, headers: dict) -> None:
    try:
        with requests.Session() as session:
            response = session.get(url=url, headers=headers, timeout=60)
            print(response.status_code)
    except Exception as ex:
        print(ex)


def main():
    session = requests.Session()
    # html = get_html(url=url, headers=headers, session=session)
    # get_data(url=url, headers=headers)
    # json = get_json(url=url_api, headers=headers, session=session)
    items = get_products('Видеокарты')
    print(items)
    # print(json)

if __name__ == '__main__':
    main()
