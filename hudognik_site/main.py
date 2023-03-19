import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
import csv

useragent = UserAgent()

url = "https://hudognik.net/artists/"

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}


def get_url(session, url, headers):
    try:
        response = session.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        pages_count = int(soup.find('div', class_='page_list page_list_hudognik').find_all('a')[-1].text.strip())
    except Exception as ex:
        print(ex)
        pages_count = 1

    url_list = []

    # for page in range(1, pages_count + 1):
    for page in range(1, 2):
        try:
            url = f"https://hudognik.net/artists/page{page}"
            response = session.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception as ex:
            print(ex)
            continue
        try:
            page_urls = soup.find_all(itemprop='url')
            for item in page_urls:
                url = "https://hudognik.net" + item.get('href')
                url_list.append(url)
            print(url_list)
        except Exception as ex:
            print(ex)
            continue
    with open('data/url_list.txt', 'w', encoding='utf-8') as file:
        print(*url_list, file=file, sep='\n')


def main():
    with requests.Session() as session:
        get_url(session=session, url=url, headers=headers)


if __name__ == '__main__':
    main()
