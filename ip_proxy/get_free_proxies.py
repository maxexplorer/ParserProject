import requests
import random
from bs4 import BeautifulSoup


def get_free_proxies():
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
    }
    url = "https://free-proxy-list.net/"

    # получаем ответ HTTP и создаем объект soup
    with requests.Session() as session:
        response = session.get(url=url, headers=headers, timeout=60)

    soup = BeautifulSoup(response.text, 'lxml')

    proxies = []

    try:
        items_data = soup.find('table', class_='table table-striped table-bordered').find_all('tr')
    except Exception as ex:
        print(f'items_data: {ex}')
        items_data = []

    for item in items_data:
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies

free_proxies = get_free_proxies()

print(f'Обнаружено бесплатных прокси - {len(free_proxies)}:')
for i in range(len(free_proxies)):
    print(f"{i+1}) {free_proxies[i]}")