import requests
from fake_useragent import UserAgent

useragent = UserAgent()

url = "https://cs.money/ru/market/buy/"

headers = {
    'User-Agent': useragent
}


def get_data(url, headers):
    response = requests.get(url=url, headers=headers)
    print(response.status_code)


def main():
    get_data(url=url, headers=headers)


if __name__ == '__main__':
    main()
