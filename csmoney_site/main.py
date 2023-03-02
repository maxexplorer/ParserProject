import requests
from fake_useragent import UserAgent
import json
import os

useragent = UserAgent()

# url = "https://cs.money/ru/market/buy/"
url = "https://cs.money/1.0/market/sell-orders?limit=60&offset=0&type=5"

headers = {
    'User-Agent': useragent.random
}


def get_data(url, headers):
    response = requests.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def main():
    get_data(url=url, headers=headers)


if __name__ == '__main__':
    main()
