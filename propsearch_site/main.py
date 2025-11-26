import os
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()

exceptions_data = []


def get_html(url, session):
    """
    Получает HTML-страницу через requests с заголовками.

    :param url: URL страницы
    :param session: объект requests.Session
    :return: HTML-код страницы в виде строки
    """
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    try:
        response = session.get(url=url, headers=headers)
        return response.text
    except Exception as ex:
        print(ex)
        return ""


def save_excel(data, file_name):
    """
    Сохраняет список словарей в Excel-файл с указанным именем.

    Создает папку 'results', если она не существует.
    Если файл уже существует, дописывает новые строки в конец.

    :param data: Список словарей с данными
    :param file_name: Название файла Excel
    """
    directory = 'results'
    file_path = f'{directory}/{file_name}'

    # Создаем папку results
    os.makedirs(directory, exist_ok=True)

    # Если файла нет — создаем пустой
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='Data', index=False)

    # Читаем существующие данные
    df_existing = read_excel(file_path, sheet_name='Data')
    num_existing_rows = len(df_existing.index)

    # Преобразуем новые данные в DataFrame
    new_df = DataFrame(data)

    # Дописываем новые строки в конец
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(
            writer,
            startrow=num_existing_rows + 1,
            header=(num_existing_rows == 0),
            sheet_name='Data',
            index=False
        )

    print(f'Сохранено {len(data)} записей в {file_path}')


def get_data(html, session):
    """
    Парсит HTML страницы с районами, получает ссылки на здания и собирает данные о каждом здании.
    Сохраняет данные партиями по batch_size в Excel.

    :param html: HTML-код страницы с районами
    :param session: объект requests.Session
    """
    batch_size = 100
    result_data = []

    # Получаем список районов
    soup = BeautifulSoup(html, 'lxml')
    district_items = soup.find('div', class_='grid md:grid-cols-2 gap-x-6 gap-y-8').find_all('a')
    count_districts = len(district_items)

    for i, district_item in enumerate(district_items, 1):
        try:
            url = district_item.get('href')
            html = get_html(url=url, session=session)
            soup = BeautifulSoup(html, 'lxml')
            building_items = set(soup.find_all(class_='lg:px-2 py-1 h-full'))
        except Exception as ex:
            print(ex)
            continue

        # Обрабатываем каждое здание в районе
        for c in building_items:
            try:
                url = c.find('a').get('href')
                html = get_html(url=url, session=session)
                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(ex)
                continue

            # Собираем данные по зданию
            try:
                building_name = soup.find('h1', class_='ps-h1').get_text(strip=True)
            except Exception as ex:
                exceptions_data.append({'URL': url, 'Error': str(ex)})
                continue

            try:
                building_overview = ' '.join(
                    soup.find('div', class_='lg:text-xl mx-auto max-w-160').get_text(strip=True).split())
            except Exception:
                building_overview = None

            try:
                img_link = soup.find('img', title=building_name).get('src')
            except Exception:
                img_link = None

            # Остальные поля
            try:
                building_type = ' '.join(soup.find('div', string=re.compile('Building type')).find_next().text.split())
            except Exception:
                building_type = None

            try:
                status = ' '.join(soup.find('div', string=re.compile('Status')).find_next().text.split())
            except Exception:
                status = None

            try:
                floors = soup.find('div', string=re.compile('Floors')).find_next().get_text(strip=True)
            except Exception:
                floors = None

            try:
                area = soup.find('div', text='Area').find_next().get_text(strip=True)
            except Exception:
                area = None

            try:
                sub_buildings = ' '.join(soup.find('div', string=re.compile('Sub-buildings')).find_next().text.split())
            except Exception:
                sub_buildings = None

            try:
                developer = soup.find('div', string=re.compile('The developer')).find_next().get_text(strip=True)
            except Exception:
                developer = None

            try:
                timeline = soup.find('div', string=re.compile('Timeline')).find_next().get_text(strip=True)
            except Exception:
                timeline = None

            try:
                plot = soup.find('div', string=re.compile('Plot')).find_next().get_text(strip=True)
            except Exception:
                plot = None

            try:
                units = soup.find('div', string=re.compile('Units')).find_next().get_text(strip=True)
            except Exception:
                units = None

            try:
                unit_layouts = soup.find('div', string=re.compile('Unit layouts')).find_next().get_text(strip=True)
            except Exception:
                unit_layouts = None

            try:
                architect = soup.find('div', string=re.compile('The architect')).find_next().get_text(strip=True)
            except Exception:
                architect = None

            try:
                contractor = soup.find('div', string=re.compile('The contractor')).find_next().get_text(strip=True)
            except Exception:
                contractor = None

            try:
                structure = soup.find('div', string=re.compile('Structure')).find_next().get_text(strip=True)
            except Exception:
                structure = None

            try:
                amenities = soup.find('div', string=re.compile('Amenities')).find_next().get_text(strip=True)
            except Exception:
                amenities = None

            try:
                additional_information = ' '.join(
                    soup.find('div', string=re.compile('Additional information')).find_next().text.split())
            except Exception:
                additional_information = None

            try:
                commute_times_by_car = soup.find('div',
                                                 string=re.compile('Commute times by car')).find_next().get_text(strip=True)
            except Exception:
                commute_times_by_car = None

            try:
                airport_proximity = soup.find('div', string=re.compile('Airport proximity')).find_next().get_text(strip=True)
            except Exception:
                airport_proximity = None

            try:
                map_coordinates = soup.find('iframe').get('src').split('=')[-2].replace('&zoom', '').strip()
            except Exception:
                map_coordinates = None

            # Остальные категории: attractions, parks, golf, cinemas и т.д.
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

            # Социальная инфраструктура
            try:
                shops_and_outlets = ''
                for i in [item.text.split() for item in
                          soup.find_all('div', class_='flex flex-col justify-between h-full')]:
                    shops_and_outlets += ' '.join(i)
            except Exception:
                shops_and_outlets = None

            try:
                supermarkets_and_mini_marts = ''
                for i in [item.get_text(strip=True).split() for item in
                          soup.find('span', string=re.compile('Supermarkets & Mini Marts')).find_next()]:
                    supermarkets_and_mini_marts += ' '.join(i)
            except Exception:
                supermarkets_and_mini_marts = None

            try:
                restaurants_and_bars = ''
                for i in [item.get_text(strip=True).split() for item in
                          soup.find('span', string=re.compile('Restaurants & Bars')).find_next()]:
                    restaurants_and_bars += ' '.join(i)
            except Exception:
                restaurants_and_bars = None

            try:
                clinics_and_pharmacies = ''
                for i in [item.get_text(strip=True).split() for item in
                          soup.find('span', string=re.compile('Clinics & Pharmacies')).find_next()]:
                    clinics_and_pharmacies += ' '.join(i)
            except Exception:
                clinics_and_pharmacies = None

            try:
                salons_and_spas = ''
                for i in [item.get_text(strip=True).split() for item in
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
                for i in [item.text.replace('Read more', ' ').split() for item in soup.find_all('div',
                                                                                                class_='ml-4 md:ml-6 md:-mr-2 lg:ml-0 lg:mr-4 snap-start flex-none w-[274px] pb-2')]:
                    nearby_neighbourhoods += ' '.join(i)
            except Exception:
                nearby_neighbourhoods = None

            # Добавляем данные здания в результат
            result_data.append(
                {
                    'area': area,
                    'building_name': building_name,
                    'building_overview': building_overview,
                    'building_type': building_type,
                    'status': status,
                    'floors': floors,
                    'sub_buildings': sub_buildings,
                    'developer': developer,
                    'timeline': timeline,
                    'plot': plot,
                    'units': units,
                    'unit_layouts': unit_layouts,
                    'architect': architect,
                    'contractor': contractor,
                    'structure': structure,
                    'amenities': amenities,
                    'additional_information': additional_information,
                    'commute_times_by_car': commute_times_by_car,
                    'airport_proximity': airport_proximity,
                    'map_coordinates': map_coordinates,
                    'attractions': attractions,
                    'parks_and_beaches': parks_and_beaches,
                    'golf_and_clubs': golf_and_clubs,
                    'cinemas': cinemas,
                    'shops_and_outlets': shops_and_outlets,
                    'supermarkets_and_mini_marts': supermarkets_and_mini_marts,
                    'restaurants_and_bars': restaurants_and_bars,
                    'clinics_and_pharmacies': clinics_and_pharmacies,
                    'salons_and_spas': salons_and_spas,
                    'local_schools': local_schools,
                    'nearby_neighbourhoods': nearby_neighbourhoods,
                    'url': url,
                    'img_link': img_link
                }
            )

            # Сохраняем пакет данных
            if len(result_data) >= batch_size:
                save_excel(result_data, 'result_data.xlsx')
                result_data.clear()

            print(f'District: {area}, Building: {building_name}')

        print(f'Обработано районов: {i}/{count_districts}')

    # Сохраняем оставшиеся данные
    if result_data:
        save_excel(result_data, 'result_data.xlsx')


def main():
    """
    Основная функция запуска скрипта.
    Открывает сессию, получает HTML, парсит данные и сохраняет исключения.
    """
    with requests.Session() as session:
        html = get_html(url="https://propsearch.ae/dubai/buildings", session=session)
        get_data(html=html, session=session)

    # Сохраняем исключения
    if exceptions_data:
        save_excel(exceptions_data, 'exception_list.xlsx')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
