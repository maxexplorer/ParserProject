import os
import time
from datetime import datetime

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}


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


def get_products_urls(url: str, headers: dict) ->list[dict]:
    product_data_list = []

    with Session() as session:
        try:
            html = get_html(url=url, headers=headers, session=session)
        except Exception as ex:
            print(f'get_products_urls: {ex}')

        soup = BeautifulSoup(html, 'lxml')

        try:
            data = soup.find_all('li', class_='menu-item-catalog')
        except Exception as ex:
            print(f'data: {ex}')

        for item in data:
            product_urls = []
            try:
                category_name = item.find('a',  itemprop='url').text.strip()
            except Exception:
                category_name = None

            try:
                product_items = item.find('ul', class_='sub-menu').find_all('a')
            except Exception:
                continue

            for i, product_item in enumerate(product_items, 1):
                try:
                    product_url = product_item.get('href')
                except Exception:
                    continue

                product_urls.append(product_url)

                print(f'Получена ссылка: {i}')

            product_data_list.append(
                {
                    category_name: product_urls
                }
            )

            print(f'Обработана категория: {category_name}')

    return product_data_list


def get_products_data(product_data_list: list) -> list[dict]:
    result_data = []
    images_urls_list = []

    with Session() as session:
        for category_dict in product_data_list:
            for category_name, product_urls in category_dict.items():
                for product_url in product_urls:
                    try:
                        time.sleep(1)
                        html = get_html(url=product_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{product_url} - {ex}")
                        continue

                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'lxml')

                    try:
                        title = soup.find('h1').text.strip()
                    except Exception:
                        title = None

                    try:
                        price = int(
                            ''.join(filter(lambda x: x.isdigit(), soup.find('span', class_='catalogbox__price').text.strip())))
                    except Exception:
                        price = None

                    try:
                        images_items = soup.find('div', class_='catalogbox__galbox js-catalog-detail-fotorama-wrap').find_all(
                            'a')
                        for image_item in images_items:
                            image_url = f"https://bellodeco.ru/{image_item.get('href')}"
                            images_urls_list.append(image_url)
                            product_images_urls_list.append(image_url)
                        main_image_url = product_images_urls_list[0]
                        additional_images_urls = '; '.join(product_images_urls_list[1:])
                    except Exception:
                        main_image_url = None
                        additional_images_urls = None

                    try:
                        description = soup.find('div', class_='catalogbox__description').text.strip().splitlines()[-1]
                    except Exception:
                        description = None

                    try:
                        models = soup.find('div', class_='b-model-list').find_all('div', class_='model-list__item')
                        try:
                            model_fbx = models[0].find('a').get('href')
                        except Exception:
                            model_fbx = None
                        try:
                            model_obj = models[1].find('a').get('href')
                        except Exception:
                            model_obj = None
                        try:
                            model_3ds = models[2].find('a').get('href')
                        except Exception:
                            model_3ds = None
                    except Exception:
                        pass

                    result_dict = {
                        'Название товара': title,
                        'Ссылка': product_url,
                        'Цена': price,
                        'Главное изображение': main_image_url,
                        'Дополнительные изображения': additional_images_urls,
                        'Описание': description,
                        'Модель fbs': model_fbx,
                        'Модель obj': model_obj,
                        'Модель 3ds': model_3ds,
                    }

                    # Сбор параметров товара
                    product_parameters = {}
                    try:
                        parameters_items = soup.find('div', class_='catalogbox__param__left').find_all('div')
                        for parameter_item in parameters_items:
                            attribute_name = parameter_item.text.split(':')[0].strip()
                            attribute_value = parameter_item.text.split(':')[1].strip()
                            product_parameters[attribute_name] = attribute_value
                    except Exception:
                        pass

                    # Сбор характеристик товара
                    product_characteristics = {}
                    try:
                        characteristics_items = soup.find('div', id='tabs-obj_description').find_all('tr')
                        for characteristic_item in characteristics_items:
                            characteristic = characteristic_item.find_all('td')
                            attribute_name = characteristic[0].text.strip()
                            attribute_value = characteristic[1].text.strip()
                            product_characteristics[attribute_name] = attribute_value
                    except Exception:
                        pass

                    product_attributes = {**product_parameters, **product_characteristics}

                    result_dict.update(product_attributes)

                    result_data.append(result_dict)

                    print(f'Обработано: {j}/{count_urls}')

        if not os.path.exists('data'):
            os.mkdir('data')

        with open('data/images_urls_list.txt', 'w', encoding='utf-8') as file:
            print(*images_urls_list, file=file, sep='\n')

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    product_data_list = get_products_urls(url="https://neftemash-m.com/catalog/", headers=headers)
    result_data = get_products_data(product_data_list=product_data_list)
    # save_excel(data=result_data, species='products')

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
