import requests
from bs4 import BeautifulSoup
import time


def test_request(url, retry=5):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.67 Safari/537.36'
    }
    try:
        response = requests.get(url=url, headers=headers)
        print(f'[+] {url} {response.status_code}')
    except Exception:
        time.sleep(3)
        if retry:
            print(f'[INFO] retry={retry}=>{url}')
            return test_request(url, retry=(retry - 1))
        else:
            raise
    else:
        return response


def main():
    with open('data/books_urls.txt') as file:
        book_urls = file.read().splitlines()

        for book_url in book_urls:
            try:
                r = test_request(url=book_url)
                soup = BeautifulSoup(r.text, 'lxml')
                print(f'{soup.title.text}\n{"_" * 20}')
            except Exception:
                continue


if __name__ == '__main__':
    main()
