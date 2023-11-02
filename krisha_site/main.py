import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
from pandas import DataFrame, ExcelWriter
import openpyxl

url = "https://krisha.kz/prodazha/kvartiry/?das[house.year][to]=2023&das[price][from]=90000000&das[who]=1"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}


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
        pages = int(soup.find_all('a', class_='paginator__btn')[-2].text.strip())
        return pages
    except Exception as ex:
        print(ex)


def get_data(session, pages):
    for i in range(1, pages + 1)[:1]:
        url = f"https://krisha.kz/prodazha/kvartiry/?das[house.year][to]=2023&das[price][from]=90000000&das[who]=" \
              f"1&page={i}"

        html = get_html(url=url, headers=headers, session=session)

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.select('div[data-list-id=main]')
            print(data)
        except Exception as ex:
            print(ex)




def main():
    with requests.Session() as session:
        html = get_html(url=url, headers=headers, session=session)
        pages = get_pages(html)
        print(f'Total: {pages} pages')
        data = get_data(session=session, pages=pages)


if __name__ == '__main__':
    main()
