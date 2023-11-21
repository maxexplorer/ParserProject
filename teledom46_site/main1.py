import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

category_urls_list = [
    "http://teledom46.ru/catalog/televizory_audio_video/",
    "http://teledom46.ru/catalog/tekhnika_dlya_kukhni/",
    "http://teledom46.ru/catalog/vstraivaemaya_tekhnika/",
    "http://teledom46.ru/catalog/vytyazhki/",
    "http://teledom46.ru/catalog/tekhnika_dlya_doma/",
    "http://teledom46.ru/catalog/klimaticheskaya_tekhnika/",
    "http://teledom46.ru/catalog/sadovaya-tekhka/"
]

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

start_time = datetime.now()


def get_html(url, headers, session):
    try:
        response = session.get(url=url, headers=headers, timeout=60)
        html = response.text
        return html
    except Exception as ex:
        print(ex)


def get_data(file_path, headers):
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

    result_list = []

    with requests.Session() as session:
        for i, product_url in enumerate(product_urls_list[10:20], 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                article = soup.find('span', class_='article__value').text.strip()
            except Exception:
                article = None

            try:
                name = soup.find('div', class_='topic__heading').text.strip()
            except Exception:
                name = None

            try:
                folder = soup.find_all('span', class_='breadcrumbs__item-name font_xs')[2].text.strip()
            except Exception:
                folder = None

            try:
                image_data = soup.find_all('a', class_='product-detail-gallery__link popup_link fancy')

                image = ''
                for item in image_data:
                    try:
                        url = "http://teledom46.ru" + item.get('href')
                        image += f'{url}, '
                    except Exception:
                        image = None

            except Exception as ex:
                print(ex)
                continue

            try:
                price = soup.find('span', class_='price_value').text.strip().replace(' ', ' ')
            except Exception:
                price = None

            try:
                characteristic = ' '.join(soup.find('div', class_='char-side').text.strip().split())
            except Exception:
                characteristic = None

            try:
                description = ' '.join(
                    soup.find('div', {'class': 'content', 'itemprop': 'description'}).text.strip().split())
            except Exception:
                description = None

            body = f'{characteristic} {description}'

            result_list.append(
                (
                    body,
                    name,
                    article,
                    price,
                    folder,
                    image
                )
            )

            print(f'Обработано товаров: {i}')
    print(result_list)

    return result_list


def save_csv(data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            (
                'body: Описание',
                'name: Название',
                'article: Артикул',
                'price: Цена',
                'folder: Категория',
                'image: Иллюстрация'
            )
        )

    with open(f'data/data_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    result_list = get_data(file_path="data/product_url_list.txt", headers=headers)
    save_csv(data=result_list)

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
