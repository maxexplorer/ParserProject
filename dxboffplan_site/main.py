import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import re

start_time = datetime.now()

exceptions_list = []


def get_html(url, session):
    headers = {
        'Accept': '*/*',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
    }

    try:
        response = session.get(url=url, headers=headers)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_data(html, session):
    result_list = []
    price_range_list = []

    soup = BeautifulSoup(html, 'lxml')
    developer_items = soup.find('div', class_='developments-table').find_all('div', class_='item')
    for i in developer_items:
        try:
            developer_data = i.find_all('span')
        except Exception as ex:
            print(f'developer_data - {ex}')
            continue
        try:
            developer_name = i.find('a').get_text(strip=True)
        except Exception:
            developer_name = None
        if not developer_name:
            continue
        try:
            projects_count = developer_data[0].get_text(strip=True)
            if projects_count == '0':
                continue
        except Exception:
            projects_count = None
        try:
            min_price = developer_data[1].get_text(strip=True)
        except Exception:
            min_price = None
        try:
            max_price = developer_data[2].get_text(strip=True)
        except Exception:
            max_price = None
        try:
            avg_price = developer_data[3].get_text(strip=True)
        except Exception:
            avg_price = None
        try:
            developer_url = i.find('a').get('href')
            html = get_html(url=developer_url, session=session)
            soup = BeautifulSoup(html, 'lxml')
            project_items = soup.find('section', class_='developments-table single-developer-table').find_all('div', class_='item')
        except Exception as ex:
            print(f'url_developer - {ex}')
            continue
        for c in project_items:
            try:
                project_name = c.find('a').get_text(strip=True)
            except Exception:
                project_name = None
            if not project_name:
                continue
            try:
                property_type = c.find('span', class_='text-capitalize').get_text(strip=True)
            except Exception:
                property_type = None
            try:
                project_url = c.find('a').get('href')
                html = get_html(url=project_url, session=session)
                soup = BeautifulSoup(html, 'lxml')
            except Exception as ex:
                print(f'url_project - {ex}')
                continue
            try:
                starting_price = soup.find('div', string=re.compile('Start price from')).find_next().get_text(strip=True)
            except Exception as ex:
                starting_price = None
                exceptions_list.append(
                    (developer_url, project_url, ex)
                )
            try:
                price_per_sqft_from = soup.find('div', string=re.compile('Price Per Sqft from')).find_next().get_text(strip=True)
            except Exception:
                price_per_sqft_from = None
            try:
                area_from = soup.find('div', string=re.compile('Area from')).find_next().get_text(strip=True)
            except Exception:
                area_from = None
            try:
                type = soup.find('div', string=re.compile('Type')).find_next().get_text(strip=True)
            except Exception:
                type = None
            try:
                bedrooms = soup.find('div', string=re.compile('Bedrooms')).find_next().get_text(strip=True)
            except Exception:
                bedrooms = None
            try:
                location = soup.find('div', string=re.compile('Location')).find_next().get_text(strip=True)
            except Exception:
                location = None
            try:
                completion = soup.find('div', string=re.compile('Est. Completion')).find_next().get_text(strip=True)
            except Exception:
                completion = None
            try:
                images_items = soup.find('div', class_='gallery-grid').find_all('div', class_='thickbox setThumbMe')
                images_urls = [image_item.find('img').get('data-lazy-src') for image_item in images_items]
            except Exception:
                images_urls = None

            result_list.append(
                (
                    developer_name,
                    projects_count,
                    min_price,
                    max_price,
                    avg_price,
                    project_name,
                    property_type,
                    starting_price,
                    price_per_sqft_from,
                    area_from,
                    type,
                    bedrooms,
                    location,
                    completion,
                    developer_url,
                    project_url,
                    images_urls
                )
            )

            try:
                price_range_items = soup.find('div', class_='prices-items').find_all('div', class_='prices-items')
            except Exception:
                continue
            for item in price_range_items:
                try:
                    type_apartment = ' '.join(item.find('li', class_='first-appart').text.strip().split())
                except Exception:
                    type_apartment = None
                try:
                    size_apartment = '-'.join(
                        item.find('li', class_='size-appart').text.strip().replace('Size from - to (Sqft.)',
                                                                                   '').replace(
                            'Created with Fabric.js 1.7.22', '').replace('Sqft', '').split())
                except Exception:
                    size_apartment = None
                try:
                    price_apartment = '-'.join(
                        item.find('li', class_='price-appart').text.strip().replace('Price from - to', '').replace(
                            'Ask for Price', '').split())
                except Exception:
                    price_apartment = None

                price_range_list.append(
                    (
                        project_url,
                        type_apartment,
                        size_apartment,
                        price_apartment
                    )
                )

            print(f'Developer: {developer_name}, Project: {project_name}')

    return result_list


def save_csv_data(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_dxboffplan_1.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Developer name',
                'Projects count',
                'Min price',
                'Max price',
                'Avg price',
                'Project name',
                'Property type',
                'Starting price',
                'Price per sqft from',
                'Area from',
                'Type',
                'Bedrooms',
                'Location',
                'Completion',
                'Developer link',
                'Project link',
                'Images links'

            )
        )

    with open('data/data_dxboffplan_1.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def save_csv_price(price):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/price_dxboffplan.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Project link',
                'Type',
                'Size',
                'Price'
            )
        )

    with open('data/price_dxboffplan.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            price
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    with requests.Session() as session:
        html = get_html(url="https://dxboffplan.com/list-of-property-developers-in-uae/", session=session)
        data = get_data(html=html, session=session)
        save_csv_data(data)
        # save_csv_price(price)
    if len(exceptions_list) > 0:
        with open(f'data/exceptions_list.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(exceptions_list)
    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
