import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
import csv

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}


def get_url(headers):
    url = "https://hudognik.net/artists/"

    response = requests.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)


def main():
    get_url(headers=headers)


if __name__ == '__main__':
    main()
