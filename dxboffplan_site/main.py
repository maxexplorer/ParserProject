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
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_8; ja-jp) AppleWebKit/533.16 (KHTML, like Gecko)'
                      ' Version/5.0 Safari/533.16'
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
    developer_items = soup.find('tbody').find_all('tr')
    for i in developer_items:
        try:
            developer_data = i.find_all('td')
        except Exception as ex:
            print(f'developer_data - {ex}')
            continue
        try:
            developer_name = developer_data[0].find_next().text.strip()
        except Exception:
            developer_name = None
        try:
            projects_count = developer_data[1].text.strip()
            if projects_count == '0':
                continue
        except Exception:
            projects_count = None
        try:
            min_price = developer_data[2].text.strip()
        except Exception:
            min_price = None
        try:
            max_price = developer_data[3].text.strip()
        except Exception:
            max_price = None
        try:
            avg_price = developer_data[4].text.strip()
        except Exception:
            avg_price = None
        try:
            developer_url = i.find('a').get('href')
            html = get_html(url=developer_url, session=session)
            soup = BeautifulSoup(html, 'lxml')
            project_urls = soup.find('tbody').find_all('tr')
        except Exception as ex:
            print(f'url_developer - {ex}')
            continue
        for c in project_urls:
            try:
                project_name = c.find('a').text.strip()
            except Exception:
                project_name = None
            try:
                property_type = c.find_all('td')[2].text.strip()
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
                starting_price = soup.find('th', string=re.compile('Starting Price')).find_next().text.strip()
            except Exception as ex:
                starting_price = None
                exceptions_list.append(
                    (developer_url, project_url, ex)
                )
            try:
                price_per_sqft_from = soup.find('th', string=re.compile('Price Per Sqft from')).find_next().text.strip()
            except Exception:
                price_per_sqft_from = None
            try:
                area_from = soup.find('th', string=re.compile('Area from')).find_next().text.strip()
            except Exception:
                area_from = None
            try:
                type = soup.find('th', string=re.compile('Type')).find_next().text.strip()
            except Exception:
                type = None
            try:
                bedrooms = soup.find('th', string=re.compile('Bedrooms')).find_next().text.strip()
            except Exception:
                bedrooms = None
            try:
                location = soup.find('th', string=re.compile('Location')).find_next().text.strip()
            except Exception:
                location = None
            try:
                completion = soup.find('th', string=re.compile('Est. Completion')).find_next().text.strip()
            except Exception:
                completion = None
            try:
                images = tuple(img.get('src') for img in soup.select('img[decoding=async]'))
            except Exception:
                images = None

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
                    images
                )
            )

            # try:
            #     price_range_items = soup.find('div', class_='project-price-range my-3').find_all('ul')
            # except Exception:
            #     continue
            # for item in price_range_items:
            #     try:
            #         type_apartment = ' '.join(item.find('li', class_='first-appart').text.strip().split())
            #     except Exception:
            #         type_apartment = None
            #     try:
            #         size_apartment = '-'.join(
            #             item.find('li', class_='size-appart').text.strip().replace('Size from - to (Sqft.)',
            #                                                                        '').replace(
            #                 'Created with Fabric.js 1.7.22', '').replace('Sqft', '').split())
            #     except Exception:
            #         size_apartment = None
            #     try:
            #         price_apartment = '-'.join(
            #             item.find('li', class_='price-appart').text.strip().replace('Price from - to', '').replace(
            #                 'Ask for Price', '').split())
            #     except Exception:
            #         price_apartment = None
            #
            #     price_range_list.append(
            #         (
            #             project_url,
            #             type_apartment,
            #             size_apartment,
            #             price_apartment
            #         )
            #     )

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
        data, price = get_data(html=html, session=session)
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
