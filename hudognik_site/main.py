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


def get_urls(session, url, headers):
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
        except Exception as ex:
            print(ex)
            continue
    with open('data/url_list.txt', 'w', encoding='utf-8') as file:
        print(*url_list, file=file, sep='\n')


def get_data_artists(session, headers):
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     list_urls = [line.strip() for line in file.readlines()]

    # urls_count = len(list_urls)
    result_data = []

    # for i, url in enumerate(list_urls):
    for i, url in enumerate(['https://hudognik.net/artist13147/']):
        try:
            response = session.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception as ex:
            print(ex)
            continue
        try:
            artist_name = soup.find('h1', itemprop='name').text.strip()
        except Exception:
            artist_name = None
        try:
            phone = soup.find('div', class_='hudognik_menu')
        except:
            phone = None
        try:
            country_city = ','.join(
                soup.find('ul', class_='hudognik_about').text.replace('Страна', '').replace('Город', '').split(':')
                [-2:])
        except Exception:
            country_city = None
        try:
            rating = int(soup.find('span', class_='cgray').next_sibling.text)
        except Exception:
            rating = None

        print(artist_name, country_city, rating, phone)


def main():
    with requests.Session() as session:
        # get_urls(session=session, url=url, headers=headers)
        get_data_artists(session=session, headers=headers)


if __name__ == '__main__':
    main()
