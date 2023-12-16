import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

useragent = UserAgent()

headers = {
    'Accept': '*/*',
    'User-Agent': useragent.random
}

proxies = {
    'http': 'http://141.145.214.176:80',

}


def get_ip():
    # response = requests.get(url="https://api.2ip.me/provider.json", headers=headers, proxies=proxies)
    session = requests.Session()
    session.proxies.update(proxies)
    session.headers.update(headers)
    response = session.get(url="https://2ip.ru/")

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
