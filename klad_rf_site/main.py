import requests
from bs4 import BeautifulSoup
import os
import json
from pandas import DataFrame, ExcelWriter
import openpyxl

url = "https://kladr-rf.ru/"
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36'
}


def get_html(url, headers):
    response = requests.get(url=url, headers=headers)
    html = response.text
    return html


def get_data(html):
    city_streets = []

    soup = BeautifulSoup(html, 'lxml')

    items = soup.find('div', class_='pb-2 fs-5 fw-bold border-bottom', text='Города').find_next().find_all('li')

    for item in items:
        if 'class="old"' in str(item) or 'class="del"' in str(item):
            continue
        try:
            url = "https://kladr-rf.ru" + item.find('a').get('href')
            city = item.text.strip().strip()
            print(city)
            html_city = get_html(url=url, headers=headers)
            soup = BeautifulSoup(html_city, 'lxml')
            streets = soup.find(class_='pb-2 fs-5 fw-bold border-bottom', text='Улицы').find_next().find_all('li')
            for street in streets:
                if 'class="old"' in str(item) or 'class="del"' in str(item):
                    continue
                city_streets.append(
                    {

                        'Город': city,
                        'Улица': street.text.strip()
                    }
                )
        except Exception:
            continue
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find('div', class_='pb-2 fs-5 fw-bold border-bottom', text='Районы').find_next().find_all('li')

    for item in items:
        if 'class="old"' in str(item) or 'class="del"' in str(item):
            continue
        try:
            url = "https://kladr-rf.ru" + item.find('a').get('href')
            html_district = get_html(url=url, headers=headers)
            soup = BeautifulSoup(html_district, 'lxml')
            items = soup.find('div', class_='pb-2 fs-5 fw-bold border-bottom', text='Города').find_next().find_all('li')
            for item in items:
                if 'class="old"' in str(item) or 'class="del"' in str(item):
                    continue
                url = "https://kladr-rf.ru" + item.find('a').get('href')
                city = item.text.strip().strip()
                print(city)
                html_city = get_html(url=url, headers=headers)
                soup = BeautifulSoup(html_city, 'lxml')
                streets = soup.find(class_='pb-2 fs-5 fw-bold border-bottom', text='Улицы').find_next().find_all('li')
                for street in streets:
                    if 'class="old"' in str(item) or 'class="del"' in str(item):
                        continue
                    city_streets.append(
                        {

                            'Город': city,
                            'Улица': street.text.strip()
                        }
                    )
        except Exception:
            continue

    return city_streets


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_excel(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    dataframe = DataFrame(data)

    writer = ExcelWriter('data/data.xlsx')
    dataframe.to_excel(writer, 'data')
    writer.save()
    print(f'Данные сохранены в файл "data.xlsx"')


def main():
    result_list = []
    for i in range(1, 90):
        if i in (80, 81, 82, 84, 85, 88):
            continue
        url = f"https://kladr-rf.ru/{str(i).zfill(2)}/"
        html = get_html(url=url, headers=headers)
        result_list.extend(get_data(html))
        print(f'Обработано {i} страниц!!!')

    save_json(result_list)
    save_excel(result_list)


if __name__ == '__main__':
    main()
