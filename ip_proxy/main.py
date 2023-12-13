import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

useragent = UserAgent()

headers = {
    'Accept': '*/*',
    'User-Agent': useragent.random
}

proxies = {
    'http': 'http://66.225.254.16:80'
}


def get_html():
    response = requests.get(url="https://sitespy.ru/my-ip", headers=headers, proxies=proxies, timeout=60)

    return response.text


def get_data(html):
    soup = BeautifulSoup(html, 'lxml')

    ip = soup.find('span', class_='ip').text.strip()
    ua = soup.find('span', class_='ip').find_next_sibling('span').text.strip()

    print(ip)
    print(ua)


def main():
    html = get_html()
    get_data(html=html)


if __name__ == '__main__':
    main()
