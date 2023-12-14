import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

useragent = UserAgent()

headers = {
    'Accept': '*/*',
    'User-Agent': useragent.random
}

proxies = {
    'http': 'http://34.77.56.122:8080'
}


def get_ip():
    response = requests.get(url="https://api.2ip.me/provider.json", headers=headers, proxies=proxies)

    print(response.json()['ip'])

    return response.text


def main():
    html = get_html()


if __name__ == '__main__':
    main()
