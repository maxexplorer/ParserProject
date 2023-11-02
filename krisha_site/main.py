import requests
import os
from bs4 import BeautifulSoup


url = "https://krisha.kz/prodazha/kvartiry/?das[house.year][to]=2023&das[price][from]=90000000&das[who]=1"



def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='pages').find_all('a')[-1].get('href').split('=')[-1])
    except Exception:
        pages = 1
    return pages


def main():
    pass


if __name__ == '__main__':
    main()