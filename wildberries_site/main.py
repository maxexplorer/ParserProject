import requests
from bs4 import BeautifulSoup
import os
import time
import json

url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru.json"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/108.0.0.0 Safari/537.36'
}

def get_data(url, headers):
    response = requests.get(url=url, headers=headers)

    data = response.json()




def main():
    get_data(url=url, headers=headers)

if __name__ == '__main__':
    main()

