import requests
import os
import json
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime


url = "http://teledom46.ru/"
# url = "https://pcshop33.ru/"

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


def get_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pages = int(soup.find('div', class_='module-pagination').find_all('a')[-2].text)
    except Exception:
        pages = 1
    return pages


def get_urls(category_urls_list, headers):
    count_urls = len(category_urls_list)
    print(f'Всего: {count_urls} категорий')

    product_urls_list = []

    with requests.Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)
            print(f'В {i} категории: {pages} страниц')

            for page in range(1, pages + 1):
                product_url = f"{category_url}?PAGEN_1={page}"
                try:
                    time.sleep(1)
                    html = get_html(url=product_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{url} - {ex}")
                    continue
                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find_all('a', class_='thumb shine')
                    for item in data:
                        try:
                            url = "http://teledom46.ru" + item.get('href')
                        except Exception as ex:
                            print(ex)
                            continue
                        product_urls_list.append(url)
                except Exception as ex:
                    print(ex)

                print(f'Обработано: {page}/{pages} страниц')

            print(f'Обработано: {i}/{count_urls} категорий')

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/product_url_list.txt', 'w', encoding='utf-8') as file:
            print(*product_urls_list, file=file, sep='\n')


def get_data(file_path, headers):
    with open(file_path, 'r', encoding='utf-8') as file:
        product_urls_list = [line.strip() for line in file.readlines()]

        count_urls = len(product_urls_list)

    result_list = []
    image_list = []
    with requests.Session() as session:
        for j, product_url in enumerate(product_urls_list[0:10], 1):
            try:
                html = get_html(url=product_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                article_number = soup.find('span', class_='article__value').text.strip()
            except Exception:
                article_number = None

            try:
                title = soup.find('div', class_='topic__heading').text.strip()
            except Exception:
                title = None

            try:
                image_data = soup.find_all('a', class_='product-detail-gallery__link popup_link fancy')

                for item in image_data:
                    try:
                        img_url = "http://teledom46.ru" + item.get('href')
                    except Exception:
                        img_url = None
                    image_list.append(
                        {
                            article_number: img_url
                        }
                    )
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


            result_list.append(
                (
                    article_number,
                    title,
                    price,
                    characteristic,
                    description
                )
            )


    return result_list, image_list

def download_imgs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        image_dict = json.load(file)

    count_urls = len(image_dict)
    count = 1

    for item in image_dict:
        for art_num, img_url in item.items():
            img_title = img_url.split('/')[-1].split('.')[0]
            response = requests.get(url=img_url)

            if not os.path.exists(f"images/{art_num}"):
                os.makedirs(f"images/{art_num}")

            with open(f"images/{art_num}/{img_title}.png", "wb") as file:
                file.write(response.content)

        print(f'Обработано изображений: {count}/{count_urls}')

        count += 1

def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/image_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print('Данные сохранены в файл "data.json"')


def save_csv(data):
    cur_date = datetime.now().strftime('%d-%m-%Y')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/data_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Артикул',
                'Название',
                'Цена',
                'Характеристики',
                'Описание'
            )
        )

    with open(f'data/data_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            data
        )
    print('Данные сохранены в файл "data.csv"')


def main():
    # get_urls(category_urls_list=category_urls_list, headers=headers)
    # result_list, image_data = get_data(file_path="data/product_url_list.txt", headers=headers)
    # save_json(data=image_data)
    # save_csv(data=result_list)
    download_imgs(file_path="data/image_data.json")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
