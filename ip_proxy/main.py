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
        'http': 'socks5://192.252.220.92:17328',
        'https': 'socks5://192.252.220.92:17328',
    }

    # session.proxies.update(proxies)
    # session.headers.update(headers)
    response = session.get(url="https://2ip.ru/", timeout=10)
    # response = session.get(url="https://api.2ip.me/provider.json", headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.text, 'lxml')

    ip = soup.find('div', class_='ip').text.strip()
    location = ' '.join(soup.find('div', class_='value-country').text.split()[:-1])

    # print(response.json()['ip'])
    print(f'IP: {ip}\nLocation: {location}')

    return response.text


def main():
    # ip = get_ip()
    import requests
    import random

    ip_addresses = ["mysuperproxy.com:5000", "mysuperproxy.com:5001", "mysuperproxy.com:5100", "mysuperproxy.com:5010",
                    "mysuperproxy.com:5050", "mysuperproxy.com:8080", "mysuperproxy.com:8001",
                    "mysuperproxy.com:8000", "mysuperproxy.com:8050"]

    def proxy_request(request_type, url, **kwargs):
        while True:
            try:
                proxy = random.randint(0, len(ip_addresses) - 1)
                proxies = {"http": ip_addresses[proxy], "https": ip_addresses[proxy]}
                response = requests.get(request_type, url, proxies=proxies, timeout=5, **kwargs)
                print(f"Используемый в настоящее время прокси-сервер: {proxy['https']}")
            break
        except:
            print("Ошибка, ищем другой прокси-сервер")


        return response


if __name__ == '__main__':
    main()
