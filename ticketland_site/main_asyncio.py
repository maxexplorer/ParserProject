import requests
import asyncio
import aiohttp
import aiofiles
from aiocsv import AsyncWriter
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import time
import os
from main import get_urls


useragent = UserAgent()
headers = {
    'user-agent': useragent.random
}

start_time = time.time()
result_data = []

async def get_data(session, i, url, urls_count):
    async with session.get(url=url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')

        try:
            title = soup.find('div', class_='show-header__title').find('h1').text.strip()
            place = soup.find('span', class_='show-card__building').text.strip()
            date = [item.text.strip().replace(' ', ' ') for item in soup.find_all('span', class_='show-card__dm')]
            date = [f'{i} {k}' for i, k in zip(date[0::2], date[1::2])]
            time = [item.text.strip() for item in soup.find_all('span', class_='show-card__t')]
            date = [f'{d} {y}' for d, y in zip(date, time)]
            price = soup.find('span', itemprop="price").text.strip().replace(' ', '')
            images = ['https:' + item.get('data-src') for item in
                      soup.find('ul', class_='slides').find_all('img', class_='lazy-show')]
            actors = [actor.text.strip() for actor in soup.find_all('a', class_='person__modal-box')]
            description = ''.join([item.text.strip().replace('\n', '') for item in
                                   soup.find('div', itemprop='description').find_all('p')])

            result_data.append(
                {
                    'title': title,
                    'place': place,
                    'date': date,
                    'price': price,
                    'images': images,
                    'actors': actors,
                    'description': description
                }
            )
        except Exception as ex:
            print(ex)

        print(f'Обработано {i}/{urls_count}')


async def gather_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [line.strip() for line in file.readlines()]

    urls_count = len(urls_list)

    tasks = []

    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls_list, 1):
            task = asyncio.create_task(get_data(session, i, url, urls_count))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    get_urls('https://www.ticketland.ru/spectacle/')
    asyncio.get_event_loop().run_until_complete(gather_data('data/url_list.txt'))

    with open('data/result_asyncio.json', 'w', encoding='utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)

    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')

if __name__ == '__main__':
    main()
