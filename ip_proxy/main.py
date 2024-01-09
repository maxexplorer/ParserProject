import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_ip():
    useragent = UserAgent()

    session = requests.Session()

    session.headers = {
        'Accept': '*/*',
        'User-Agent': useragent.random
    }

    session.proxies = {
        'https': 'socks5://85.113.47.102:1080',
        # 'https': 'socks5://122.191.108.101:7891',
        # 'http': 'http://5.161.103.41:88',
        # 'https': 'http://5.161.103.41:88',
    }


    # session.proxies.update(proxies)
    # session.headers.update(headers)
    try:
        response = session.get(url="https://2ip.ru/", timeout=10)

    except Exception as ex:
        print(ex)

    # response = session.get(url="https://api.2ip.me/provider.json", headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.text, 'lxml')

    ip = soup.find('div', class_='ip').text.strip()
    location = ' '.join(soup.find('div', class_='value-country').text.split()[:-1])

    # print(response.json()['ip'])
    print(f'IP: {ip}\nLocation: {location}')

    return response.text


def main():
    ip = get_ip()


if __name__ == '__main__':
    main()
