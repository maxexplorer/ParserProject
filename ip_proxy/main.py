import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

useragent = UserAgent()

headers = {
    'Accept': '*/*',
    'User-Agent': useragent.random
}

proxies = {
    'http': 'http://67.43.228.250:17285',
    'https': 'http://67.43.228.250:17285',
}




def get_ip():
    session = requests.Session()
    # session.headers = {
    #     'Accept': '*/*',
    #     'User-Agent': useragent.random
    # }
    #
    # session.proxies = {
    #     'http': 'http://20.198.96.26:80',
    # }

    # session.proxies_socks = {
    #     'http': 'socks5://198.27.124.188:40000',
    #     'https': 'socks5://198.27.124.188:40000',
    # }

    # session.proxies.update(proxies)
    # session.headers.update(headers)
    response = session.get(url="https://2ip.ru/", headers=headers, proxies=proxies)
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
