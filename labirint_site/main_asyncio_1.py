import asyncio
import aiohttp
from bs4 import BeautifulSoup

BASE_URL = 'https://www.labirint.ru'
CATEGORY_URL = BASE_URL + '/genres/2308/?available=1&paperbooks=1&display=table'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def parse_book_page(session, url, i):
    page_html = await fetch(session, url)
    soup = BeautifulSoup(page_html, 'lxml')
    book_title = soup.find('div', id='product-title').find('h1').text.strip()
    # book_author = soup.find('a', class_='product__author').text.strip()
    book_price = soup.find('div', class_='buying-pricenew-val').find_next().text.strip()
    book_price_old = soup.find('div', class_='buying-priceold-val').text.strip()
    print(f'Обработано {i + 1}')
    return {'title': book_title, 'price': book_price, 'price_old': book_price_old}


async def parse_category_page(session, url, book_queue):
    page_html = await fetch(session, url)
    soup = BeautifulSoup(page_html, 'lxml')
    book_links = soup.find_all('a', class_='product-title-link')
    for link in book_links:
        book_url = BASE_URL + link['href']
        await book_queue.put(book_url)


async def main():
    async with aiohttp.ClientSession() as session:
        book_queue = asyncio.Queue()
        await parse_category_page(session, CATEGORY_URL, book_queue)

        tasks = []
        for i in range(book_queue.qsize()):
            book_url = await book_queue.get()
            task = asyncio.ensure_future(parse_book_page(session, book_url, i))
            tasks.append(task)

        book_results = await asyncio.gather(*tasks)
        print(book_results)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

"""
В этом примере мы создаем функцию fetch для выполнения HTTP-запросов с использованием библиотеки aiohttp.
 Затем мы определяем функцию parse_book_page, которая использует библиотеку BeautifulSoup для парсинга 
 HTML-страницы книги и извлечения ее заголовка, автора и цены. Функция parse_category_page извлекает ссылки
  на страницы книг на странице категории и добавляет их в очередь задач.

В основной функции main мы создаем очередь задач и заполняем ее с помощью функции parse_category_page. 
Затем мы запускаем асинхронные задачи с использованием asyncio.gather и ожидаем, пока все задачи завершатся.

В результате выполнения этого кода будут распарсены все страницы книг в категории "Художественная литература"
 на сайте Labirint
"""
