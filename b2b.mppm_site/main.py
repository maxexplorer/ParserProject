import time
from datetime import datetime
import os

from requests import Session
from bs4 import BeautifulSoup

from pandas import DataFrame, ExcelWriter

from configs import headers

start_time = datetime.now()


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: Session) -> str:
    try:
        response = session.get(url=url, headers=headers, timeout=60)

        if response.status_code != 200:
            print(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем ссылки статей
def get_product_urls(headers: dict) -> None:
    products_urls_list = []

    with Session() as session:
        try:
            time.sleep(1)
            url = f"https://b2b.mppm.ru/catalog/"
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f"{url} - {ex}")

        soup = BeautifulSoup(html, 'lxml')

        try:
            urls_items = soup.find('div', class_='alphabet__main').find_all('div', class_='alphabet__link')
        except Exception as ex:
            print(f'urls_items: {ex}')

        for i, url_item in enumerate(urls_items, 1):
            try:
                product_url_short = url_item.find('a').get('href')
                product_url = f"https://b2b.mppm.ru{product_url_short}"
                products_urls_list.append(product_url)
            except Exception as ex:
                print(f'product_url: {ex}')
                continue

            print(f'Обработано: {i} url!')

    if not os.path.exists('data'):
        os.makedirs(f'data')

    with open('data/products_urls_list', 'a', encoding='utf-8') as file:
        print(*products_urls_list, file=file, sep='\n')


# Получаем данные о продуктах
def get_data(headers: dict, json_data: dict) -> tuple[list, list]:
    title_plants_data = set()
    contacts_data = set()

    with Session() as session:
        for page in range(1, 385):
            try:
                time.sleep(1)
                response = session.post(
                    f'https://back.profiplants.ru/api/app/table-products?page={page}&per_page=50&user_coords[]=56.46249048388979&user_coords[]=37.61718750000001',
                    headers=headers,
                    json=json_data,
                )

                if response.status_code != 200:
                    print(f'page: {page} status_code: {response.status_code}')

                data = response.json()

            except Exception as ex:
                print(f"page: {page} - {ex}")
                continue

            try:
                products_data = data['products']
            except Exception as ex:
                print(f'products_data/page: {page} - {ex}')
                continue

            try:
                for item in products_data:
                    try:
                        lat_title = item['variety']['lat_title']
                    except Exception:
                        lat_title = None
                    try:
                        ru_title = item['variety']['ru_title']
                    except Exception:
                        ru_title = None

                    title_plants_data.add((ru_title, lat_title))

                    try:
                        organization = item['organization']['title']
                    except Exception:
                        organization = None

                    try:
                        contacts = item['organization']['contacts']
                    except Exception:
                        contacts = None

                    try:
                        address = contacts['address']
                    except Exception:
                        address = None

                    try:
                        email = contacts['email']
                    except Exception:
                        email = None

                    try:
                        phone = contacts['phone']
                    except Exception:
                        phone = None

                    try:
                        site = contacts['site']
                    except Exception:
                        site = None

                    contacts_data.add(
                        (
                            organization,
                            address,
                            email,
                            phone,
                            site
                        )
                    )

            except Exception as ex:
                print(print(f'products_data/page: {page} - {ex}'))
                continue

            print(f'Обработано товаров: {page}/{385}')

    title_plants_data = sorted(title_plants_data)
    contacts_data = sorted(contacts_data)

    return title_plants_data, contacts_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, sheet_name: str) -> None:
    if not os.path.exists('results'):
        os.makedirs('results')

    if not os.path.exists('results/profiplants.xlsx'):
        # Если файл не существует, создаем его с пустым DataFrame
        with ExcelWriter('results/profiplants.xlsx', mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    dataframe = DataFrame(data)

    with ExcelWriter('results/profiplants.xlsx', if_sheet_exists='replace', mode='a') as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f'Данные сохранены в файл формата xlsx')


def main():
    get_product_urls(headers=headers)

    # title_plants_data, contacts_data = get_data(headers=headers, json_data=json_data)
    #
    # save_excel(data=title_plants_data, sheet_name='Растения')
    # save_excel(data=contacts_data, sheet_name='Питомники')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
