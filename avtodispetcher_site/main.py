import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import json
import csv
import time

start_time = time.time()

useragent = UserAgent()

headers = {
    'accept': '*/*',
    'user-agent': useragent.random
}


def get_data(cities):
    count = 1
    exceptions = []


    # headers = {
    #     'accept': '*/*',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
    #                   'Safari/537.36'
    # }

    with requests.Session() as session:
        for city1, city2 in cities:
            city1, city2 = city1.strip(), city2.strip()
            if city1 == city2:
                continue
            try:
                url = f"https://www.avtodispetcher.ru/distance/?from={city1}&to={city2}"
                response = session.get(url=url, headers=headers)

                soup = BeautifulSoup(response.text, 'lxml')
                distance = soup.find('span', id='totalDistance').text.strip()
                regions = [region.get('title').split(', ')[-2] for region in
                           soup.find('table', class_='route_details').find_all('td', class_='point_name')]
                print(count)
                count += 1
                with open('data/data_1_10000.csv', 'a', encoding='cp1251', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(
                        (
                            f'{city1} ({regions[0]})',
                            f'{city2} ({regions[-1]})',
                            distance
                        )
                    )
            except Exception as ex:
                print(ex)
                exceptions.append((ex, url.replace('&to', '').split('=')[-2:]))
                continue
    print(exceptions)



def main():
    with open('data/города а-к.csv') as file:
        reader = csv.reader(file, delimiter=';')
        cities = list(reader)[:10000]
    get_data(cities)
    execution_time = round(time.time() - start_time / 3600, 3)
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
