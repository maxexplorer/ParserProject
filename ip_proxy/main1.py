import requests
from bs4 import BeautifulSoup

url = "https://sitespy.ru/my-ip"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


def get_html(url: str, headers: dict = None) -> str:
    try:
        session = requests.Session()

        session.proxies = {
            'http': 'socks5://149.102.155.62:49187',
            'https': 'socks5://149.102.155.62:49187',
        }
        response = session.get(url=url, headers=headers, timeout=3)

        if response.status_code != 200:
            print(response.status_code)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_ip(url: str, headers: dict = None) -> str:
    html = get_html(url=url, headers=headers)

    soup = BeautifulSoup(html, 'lxml')

    try:
        ip = soup.find('span', class_="ip").text.strip()
        ua = soup.find('span', class_="ip").find_next_sibling('span').text.strip()

        print(ip, ua)

    except Exception as ex:
        print(ex)


def main():
    get_ip(url=url, headers=headers)


if __name__ == '__main__':
    main()
