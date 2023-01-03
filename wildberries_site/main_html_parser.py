import requests
from bs4 import BeautifulSoup
import os
import json


headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/108.0.0.0 Safari/537.36'
}
brand = 'samsung'

url = f"https://www.wildberries.ru/brands/{brand}"

def get_html(url, headers):
    response = requests.get(url=url, headers=headers)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

def main():
    get_html(url=url, headers=headers)

if __name__ == '__main__':
    main()
