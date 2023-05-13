import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import re

start_time = datetime.now()

useragent = UserAgent()


def get_html(url, session):
    headers = {
        'accept': '*/*',
        'user-agent': useragent.random
    }
    try:
        response = session.get(url=url, headers=headers)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


exceptions_list = []


def get_data(html, session):
    result_list = []

    soup = BeautifulSoup(html, 'lxml')
    items = soup.find('div', class_='ps-items-index-container').find_all('a')
    print(f'Districts count: {len(items)}')
    for i, item in enumerate(items, 1):
        try:
            url = item.get('href')
            html = get_html(url=url, session=session)
            soup = BeautifulSoup(html, 'lxml')
            items = soup.find(string=re.compile('completed buildings')).find_next().find_next().find_all(
                class_='lg:px-2 py-1 h-full')
        except Exception as ex:
            print(ex)
            continue
        print(i)
        print(f'Buildings count: {len(items)}')
        for j, item in enumerate(items, 1):
            try:
                url = item.find('a').get('href')
                html = get_html(url=url, session=session)
                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(ex)
                continue
            try:
                building_name = soup.find('h1', class_='ps-h1').text.strip()
            except Exception as ex:
                building_name = None
                exceptions_list.append(
                    (url, ex)
                )
            try:
                building_overview = ' '.join(
                    soup.find('div', class_='lg:text-xl mx-auto max-w-160').text.strip().split())
            except Exception:
                building_overview = None
            try:
                img_link = soup.find('img', title=building_name).get('src')
            except Exception:
                img_link = None
            try:
                building_type = ' '.join(soup.find('div', string=re.compile('Building type')).find_next().text.split())
            except Exception:
                building_type = None
            try:
                status = ' '.join(soup.find('div', string=re.compile('Status')).find_next().text.split())
            except Exception:
                status = None
            try:
                floors = soup.find('div', string=re.compile('Floors')).find_next().text.strip()
            except Exception:
                floors = None
            try:
                area = soup.find('div', string=re.compile('Area')).find_next().text.strip()
            except Exception:
                area = None
            try:
                sub_buildings = ' '.join(soup.find('div', string=re.compile('Sub-buildings')).find_next().text.split())
            except Exception:
                sub_buildings = None
            try:
                developer = soup.find('div', string=re.compile('The developer')).find_next().text.strip()
            except Exception:
                developer = None
            try:
                timeline = soup.find('div', string=re.compile('Timeline')).find_next().text.strip()
            except Exception:
                timeline = None
            try:
                plot = soup.find('div', string=re.compile('Plot')).find_next().text.strip()
            except Exception:
                plot = None
            try:
                units = soup.find('div', string=re.compile('Units')).find_next().text.strip()
            except Exception:
                units = None
            try:
                architect = soup.find('div', string=re.compile('The architect')).find_next().text.strip()
            except Exception:
                architect = None
            try:
                contractor = soup.find('div', string=re.compile('The contractor')).find_next().text.strip()
            except Exception:
                contractor = None
            try:
                structure = soup.find('div', string=re.compile('Structure')).find_next().text.strip()
            except Exception:
                structure = None
            try:
                amenities = soup.find('div', string=re.compile('Amenities')).find_next().text.strip()
            except Exception:
                amenities = None
            try:
                additional_information = ' '.join(
                    soup.find('div', string=re.compile('Additional information')).find_next().text.split())
            except Exception:
                additional_information = None
            try:
                commute_times_by_car = soup.find('div',
                                                 string=re.compile('Commute times by car')).find_next().text.strip()
            except Exception:
                commute_times_by_car = None
            try:
                airport_proximity = soup.find('div', string=re.compile('Airport proximity')).find_next().text.strip()
            except Exception:
                airport_proximity = None
            try:
                map_coordinates = soup.find('iframe').get('src').split('=')[-2].replace('&zoom', '').strip()
            except Exception:
                map_coordinates = None
            try:
                attractions1 = ' '.join(
                    soup.find('div', string=re.compile('Attractions')).find_next().find_next().text.split())
                attractions2 = ' '.join(soup.find('div', string=re.compile(
                    'Attractions')).find_next().find_next_sibling().find_next().text.split())
                attractions3 = ' '.join(soup.find('div', string=re.compile(
                    'Attractions')).find_next().find_next_sibling().find_next_sibling().find_next().text.split())
                attractions = f'{attractions1}, {attractions2}, {attractions3}'
            except Exception:
                attractions = None
            try:
                parks_and_beaches1 = ' '.join(
                    soup.find('div', string=re.compile('Parks & beaches')).find_next().find_next().text.split())
                parks_and_beaches2 = ' '.join(soup.find('div', string=re.compile(
                    'Parks & beaches')).find_next().find_next_sibling().find_next().text.split())
                parks_and_beaches3 = ' '.join(soup.find('div', string=re.compile(
                    'Parks & beaches')).find_next().find_next_sibling().find_next_sibling().find_next().text.split())
                parks_and_beaches = f'{parks_and_beaches1}, {parks_and_beaches2}, {parks_and_beaches3}'
            except Exception:
                parks_and_beaches = None
            try:
                golf_and_clubs1 = ' '.join(
                    soup.find('div', string=re.compile('Golf clubs')).find_next().find_next().text.split())
                golf_and_clubs2 = ' '.join(soup.find('div', string=re.compile(
                    'Golf clubs')).find_next().find_next_sibling().find_next().text.split())
                golf_and_clubs3 = ' '.join(soup.find('div', string=re.compile(
                    'Golf clubs')).find_next().find_next_sibling().find_next_sibling().find_next().text.split())
                golf_and_clubs = f'{golf_and_clubs1}, {golf_and_clubs2}, {golf_and_clubs3}'
            except Exception:
                golf_and_clubs = None
            try:
                cinemas1 = ' '.join(soup.find('div', string=re.compile('Cinemas')).find_next().find_next().text.split())
                cinemas2 = ' '.join(soup.find('div', string=re.compile(
                    'Cinemas')).find_next().find_next_sibling().find_next().text.split())
                cinemas3 = ' '.join(soup.find('div', string=re.compile(
                    'Cinemas')).find_next().find_next_sibling().find_next_sibling().find_next().text.split())
                cinemas = f'{cinemas1}, {cinemas2}, {cinemas3}'
            except Exception:
                cinemas = None
            try:
                shops_and_outlets = ''
                for i in [item.text.split() for item in
                          soup.find_all('div', class_='flex flex-col justify-between h-full')]:
                    shops_and_outlets += ' '.join(i)
            except Exception:
                shops_and_outlets = None

            try:
                supermarkets_and_mini_marts = ''
                for i in [item.text.strip().split() for item in
                          soup.find('span', string=re.compile('Supermarkets & Mini Marts')).find_next()]:
                    supermarkets_and_mini_marts += ' '.join(i)
            except Exception:
                supermarkets_and_mini_marts = None

            try:
                restaurants_and_bars = ''
                for i in [item.text.strip().split() for item in
                          soup.find('span', string=re.compile('Restaurants & Bars')).find_next()]:
                    restaurants_and_bars += ' '.join(i)
            except Exception:
                restaurants_and_bars = None
            try:
                clinics_and_pharmacies = ''
                for i in [item.text.strip().split() for item in
                          soup.find('span', string=re.compile('Clinics & Pharmacies')).find_next()]:
                    clinics_and_pharmacies += ' '.join(i)
            except Exception:
                clinics_and_pharmacies = None
            try:
                salons_and_spas = ''
                for i in [item.text.strip().split() for item in
                          soup.find('span', string=re.compile('Salons & Spas')).find_next()]:
                    salons_and_spas += ' '.join(i)
            except Exception:
                salons_and_spas = None
            try:
                local_schools = ''
                for i in [item.text.split() for item in
                          soup.find_all('div', class_='font-bold text-sm lg:text-base leading-snug mb-1')]:
                    local_schools += ' '.join(i)
            except Exception:
                local_schools = None
            try:
                nearby_neighbourhoods = ''
                for i in [item.text.replace('Read more', ' ').split() for item in
                          soup.find_all('div',
                                        class_='ml-4 md:ml-6 md:-mr-2 lg:ml-0 lg:mr-4 snap-start flex-none w-[274px] pb-2')]:
                    nearby_neighbourhoods += ' '.join(i)
            except Exception:
                nearby_neighbourhoods = None

            result_list.append(
                (
                    area,
                    building_name,
                    building_overview,
                    building_type,
                    status,
                    floors,
                    sub_buildings,
                    developer,
                    timeline,
                    plot,
                    units,
                    architect,
                    contractor,
                    structure,
                    amenities,
                    additional_information,
                    commute_times_by_car,
                    airport_proximity,
                    map_coordinates,
                    attractions,
                    parks_and_beaches,
                    golf_and_clubs,
                    cinemas,
                    shops_and_outlets,
                    supermarkets_and_mini_marts,
                    restaurants_and_bars,
                    clinics_and_pharmacies,
                    salons_and_spas,
                    local_schools,
                    nearby_neighbourhoods,
                    url,
                    img_link

                )
            )

            print(j)
    return result_list


def save_csv(data):
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_time}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Area',
                'Building name',
                'Building overview',
                'Building type',
                'Status',
                'Floors',
                'Sub buildings',
                'Developer',
                'Timeline',
                'Plot',
                'Units',
                'Architect',
                'Contractor',
                'Structure',
                'Amenities',
                'Additional information',
                'Commute times by car',
                'Airport proximity',
                'Map coordinates',
                'Attractions',
                'Parks & beaches',
                'Golf & clubs',
                'Cinemas',
                'Shops_and_outlets',
                'Supermarkets & mini_marts',
                'Restaurants & bars',
                'Clinics & pharmacies',
                'Salons & spas',
                'Local schools',
                'Nearby neighbourhoods',
                'Link',
                'Img_link'

            )
        )

    with open('data/data.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    with requests.Session() as session:
        html = get_html(url="https://propsearch.ae/dubai/buildings", session=session)
        data = get_data(html=html, session=session)
        save_csv(data)
    if len(exceptions_list) > 0:
        with open(f'data/exceptions_list.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(exceptions_list)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
