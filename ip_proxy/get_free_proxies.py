import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime

start_time = datetime.now()


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

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

    soup = BeautifulSoup(response.text, 'lxml')

    proxies = []

    try:
        items = soup.find('table', class_='table table-striped table-bordered').find('tbody').find_all('tr')
    except Exception as ex:
        print(f'items_data: {ex}')
        items = []

    for item in items:
        tds = item.find_all("td")
        try:
            if tds[-2].text.strip() == 'yes':
                continue
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except Exception as ex:
            print(ex)
            continue

    return proxies


def main():
    cur_date = datetime.now().strftime('%d-%m-%Y')

    free_proxies = get_free_proxies()

    print(f'Обнаружено бесплатных прокси - {len(free_proxies)}:')

    if not os.path.exists('data/results'):
        os.makedirs(f'data/results')

    with open(f'data/results/{cur_date}.txt', 'w', encoding='utf-8') as file:
        print(*free_proxies, file=file, sep='\n')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')





if __name__ == '__main__':
    main()

