import requests
import os

url = "https://www.dns-shop.ru"
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)

def get_data(url, headers):
    try:
        with requests.Session() as session:
            response = session.get(url=url, headers=headers, timeout=60)
            print(response.status_code)
    except Exception as ex:
        print(ex)


def main():
    session = requests.Session()
    html = get_html(url=url, headers=headers, session=session)
    print(html)
    # get_data(url=url, headers=headers)

if __name__ == '__main__':
    main()