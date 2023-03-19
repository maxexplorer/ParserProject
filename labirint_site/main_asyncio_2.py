import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
import os
import json

url = "https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/101.0.4951.67 Safari/537.36'
}

start_time = time.time()
books_data = []


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def parse_book_page(session, url, i):
    page_html = await fetch(session, url)
    soup = BeautifulSoup(page_html, 'lxml')

    books_items = soup.find('tbody', class_='products-table__body').find_all('tr')

    for item in books_items:
        book_data = item.find_all('td')
        try:
            book_title = book_data[0].find('a').text.strip()
        except Exception:
            book_title = 'Нет названия книги'
        try:
            book_author = book_data[1].text.strip()
        except Exception:
            book_author = 'Нет автора'
        try:
            # book_publishing = book_data[2].text
            book_publishing = book_data[2].find_all('a')
            book_publishing = ':'.join([item.text for item in book_publishing])
        except Exception:
            book_publishing = 'Нет издательства'
        try:
            book_new_price = int(
                book_data[3].find('div', class_='price').find('span').find('span').text.strip().replace(' ', ''))
        except Exception:
            book_new_price = 'Нет нового прайса'
        try:
            book_old_price = int(book_data[3].find('span', class_='price-gray').text.strip().replace(' ', ''))
        except Exception:
            book_old_price = 'Нет старого прайса'
        try:
            book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
        except Exception:
            book_sale = 'Нет скидки'
        try:
            book_status = book_data[-1].text.strip()
        except Exception:
            book_status = 'Нет статуса'

        books_data.append(
            {
                'book_title': book_title,
                'book_author': book_author,
                'book_publishing': book_publishing,
                'book_new_price': book_new_price,
                'book_old_price': book_old_price,
                'book_sale': book_sale,
                'book_status': book_status
            }
        )
    print(f'Обработано {i + 1}')


async def parse_url_page(session, url, book_queue):
    page_html = await fetch(session, url)
    soup = BeautifulSoup(page_html, 'lxml')
    pages_count = int(soup.find('div', class_='pagination-number').find_all('a')[-1].text)
    for page in range(1, pages_count + 1):
        page_url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}"
        await book_queue.put(page_url)


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print('Данные сохранены в файл "data.json"')


async def main():
    async with aiohttp.ClientSession() as session:
        book_queue = asyncio.Queue()
        await parse_url_page(session, url, book_queue)

        tasks = []
        for i in range(book_queue.qsize()):
            book_url = await book_queue.get()
            task = asyncio.ensure_future(parse_book_page(session, book_url, i))
            tasks.append(task)

        await asyncio.gather(*tasks)
        save_json(books_data)
        finish_time = time.time() - start_time
        print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
