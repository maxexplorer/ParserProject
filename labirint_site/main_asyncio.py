import asyncio
import aiohttp
from bs4 import BeautifulSoup
import datetime
import csv
import json
import time
import aiofiles
from aiocsv import AsyncWriter

start_time = time.time()
books_data = []


async def get_page_data(session, page):
    url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.67 Safari/537.36'
    }

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

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
        print(f'Обработано {page}')


async def gather_data():
    url = "https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.67 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        # response = await session.get(url=url, headers=headers)
        async with session.get(url=url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            pages_count = int(soup.find('div', class_='pagination-number').find_all('a')[-1].text)

            tasks = []

            for page in range(1, pages_count + 1):
                task = asyncio.create_task(get_page_data(session, page))
                tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.get_event_loop().run_until_complete(gather_data())
    cur_time = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')

    with open(f'data/data_{cur_time}_async.json', 'a', encoding='utf-8') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)

    async with aiofiles.open(f'data/labirint_{cur_time}_async.csv', 'w', encoding='utf-8') as file:
        writer = AsyncWriter(file)
        await writer.writerow(
            (
                'Название книги',
                'Автор',
                'Издательство',
                'Цена со скидкой',
                'Цена без скидки',
                'Процент скидки',
                'Наличие на складе'
            )
        )
    for book in books_data:
        async with aiofiles.open(f'data/labirint_{cur_time}_async.csv', 'a', encoding='utf-8') as file:
            writer = AsyncWriter(file)
            await writer.writerow(
                (
                    book['book_title'],
                    book['book_author'],
                    book['book_publishing'],
                    book['book_new_price'],
                    book['book_old_price'],
                    book['book_sale'],
                    book['book_status']
                )
            )

    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    main()

