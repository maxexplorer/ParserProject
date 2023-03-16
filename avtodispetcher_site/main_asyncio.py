import asyncio
import aiohttp
import aiofiles
from aiocsv import AsyncWriter
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}

start_time = time.time()
exceptions_url = []
exceptions_find_element = []


async def get_data(session, url, city1, city2, count):
    try:
        async with session.get(url=url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            distance = soup.find('span', id='totalDistance').text.strip()
            regions = [region.get('title').split(', ')[-2] for region in
                       soup.find('table', class_='route_details').find_all('td', class_='point_name')]
            print(count)

            # async with aiofiles.open('data/data_asyncio.csv', 'a', encoding='cp1251', newline='') as file:
            #     writer = AsyncWriter(file, delimiter=';')
            #     await writer.writerow(
            #         (
            #             f'{city1} ({regions[0]})',
            #             f'{city2} ({regions[-1]})',
            #             distance
            #         )
            #     )
            with open('data/data_1_1000.csv', 'a', encoding='cp1251', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        f'{city1} ({regions[0]})',
                        f'{city2} ({regions[-1]})',
                        distance
                    )
                )
    except Exception as ex:
        print(ex, url)
        exceptions_find_element.append((ex, url))
        pass


async def gather_data(cities):
    count = 1
    tasks = []
    # headers = {
    #     'accept': '*/*',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
    #                   'Safari/537.36'
    # }
    async with aiohttp.ClientSession() as session:

        for city1, city2 in cities:
            try:
                city1, city2 = city1.strip(), city2.strip()
                if city1 == city2:
                    continue
                url = f"https://www.avtodispetcher.ru/distance/?from={city1}&to={city2}"
                task = asyncio.create_task(get_data(session, url, city1, city2, count))
                count += 1
                tasks.append(task)
            except Exception as ex:
                print(ex)
                exceptions_url.append((ex, url))
                continue
        await asyncio.gather(*tasks)


async def main():
    with open('data/города а-к.csv') as file:
        reader = csv.reader(file, delimiter=';')
        cities = list(reader)[:1000]
    await gather_data(cities)
    print(exceptions_url)
    print(exceptions_find_element)
    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
