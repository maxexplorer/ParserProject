import os
import time
from datetime import datetime

from requests import Session

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel

start_time = datetime.now()

category_urls_list = [
    "https://perfect-msk.ru/catalog/karnizy/",
    "https://perfect-msk.ru/catalog/moldingi/",
    "https://perfect-msk.ru/catalog/ugol-dlya-moldinga/",
    "https://perfect-msk.ru/catalog/plintus-napolnyy/",
    "https://perfect-msk.ru/catalog/kupola-i-rozetki/",
    "https://perfect-msk.ru/catalog/kolonny-iz-poliuretana/",
    "https://perfect-msk.ru/catalog/dekorativnye-elementy/",
    "https://perfect-msk.ru/catalog/stenovye-paneli/",
    "https://perfect-msk.ru/catalog/polukolonny-iz-poliuretana/",
    "https://perfect-msk.ru/catalog/obramleniya/",
    "https://perfect-msk.ru/catalog/pilyastry/",
    "https://perfect-msk.ru/catalog/kley/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}


# Функция инициализации объекта chromedriver
def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless_mode:
        options.add_argument("--headless=new")
    driver = Chrome(options=options)
    if not headless_mode:
        driver.maximize_window()
    driver.implicitly_wait(15)

    return driver

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


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('div', class_='pagination').find_all('a', class_='pagination__item')[-1].text.strip())
    except Exception:
        pages = 1

    return pages


def get_products_urls(category_urls_list: list, headers: dict) -> list:
    count_urls = len(category_urls_list)

    new_products_urls_list = []

    with open('data/exceptions_urls_list.txt', 'r', encoding='utf-8') as file:
        exception_urls_list = [line.strip() for line in file]

    with Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue

            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url = f"{category_url}?PAGEN_1={page}/"
                try:
                    time.sleep(1)
                    html = get_html(url=page_url, headers=headers, session=session)
                except Exception as ex:
                    print(f"{page_url} - {ex}")
                    continue

                if not html:
                    continue

                soup = BeautifulSoup(html, 'lxml')

                try:
                    data = soup.find('div', class_='products-list products-list--three').find_all('div',
                                                                                                  class_='product')
                    for item in data:
                        try:
                            product_url = f"https://perfect-msk.ru{item.find('a').get('href')}"
                        except Exception:
                            continue

                        if product_url in exception_urls_list:
                            continue
                        new_products_urls_list.append(product_url)
                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

                print(f'Обработано страниц: {page}/{pages}')

            print(f'Обработана категория {category_url}: {i}/{count_urls}')

    if not os.path.exists('data'):
        os.makedirs('data')

    with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
        print(*new_products_urls_list, file=file, sep='\n')

    return new_products_urls_list


def get_products_data(driver: Chrome, products_urls_list: list) -> list[dict]:
    count_urls = len(products_urls_list)
    result_data = []
    images_urls_list = []

    for j, product_url in enumerate(products_urls_list, 1):
        product_images_urls_list = []
        try:
            time.sleep(1)
            driver.get(url=product_url)
        except Exception as ex:
            print(f"{product_url} - {ex}")
            continue

        html = driver.page_source

        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')

        try:
            sku = soup.find('div', class_='card__code').text.strip()
        except Exception:
            sku = None

        try:
            title = soup.find('div', class_='title-page').find('h1', class_='h1').text.strip()
        except Exception:
            title = None

        try:
            price = int(soup.find('span', itemprop='price').text)
        except Exception:
            price = None

        try:
            images_items = soup.find('div', class_='card__slider-main').find_all('img', class_='card__slider-image')
            for image_item in images_items:
                src = image_item.get('src')
                image_url = f"https://perfect-msk.ru{src}"
                images_urls_list.append(image_url)
                product_images_urls_list.append(image_url)
            main_image_url = product_images_urls_list[0]
            additional_images_urls = '; '.join(product_images_urls_list[1:])
        except Exception:
            main_image_url = None
            additional_images_urls = None

        try:
            description = soup.find('div', class_='card__content').text.strip()
        except Exception:
            description = None

        result_dict = {
            'Артикул': sku,
            'Название товара': title,
            'Ссылка': product_url,
            'Цена': price,
            'Главное изображение': main_image_url,
            'Дополнительные изображения': additional_images_urls,
            'Описание': description,
        }

        # Сбор параметров товара
        product_parameters = {}
        try:
            parameters_items = soup.find('div', class_='card__details').find_all('div')
            for parameter_item in parameters_items:
                attribute_name = parameter_item.text.split(':')[0].strip()
                attribute_value = parameter_item.text.split(':')[1].strip()
                product_parameters[attribute_name] = attribute_value
        except Exception:
            pass

        result_dict.update(product_parameters)

        result_data.append(result_dict)

        print(f'Обработано: {j}/{count_urls}')

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/images_urls_list.txt', 'w', encoding='utf-8') as file:
        print(*images_urls_list, file=file, sep='\n')

    return result_data

def get_products_price(products_urls_list: list, headers: dict) -> list[dict]:
    count_urls = len(products_urls_list)
    count = 1
    result_data = []

    with Session() as session:
        for title, product_url in products_urls_list:
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
                price = int(soup.find('span', itemprop='price').text)
            except Exception:
                price = None

            result_data.append(
                {
                    'Название товара': title,
                    'Ссылка': product_url,
                    'Цена': price,
                }
            )

            print(f'Обработано: {count}/{count_urls}')
            count += 1

    return result_data


def download_imgs(file_path: str, headers: dict) -> None:
    directory = 'images'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'r', encoding='utf-8') as file:
        image_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(image_urls_list)

    for k, image_url in enumerate(image_urls_list, 1):
        image_title = image_url.split('/')[-1]

        with Session() as session:
            time.sleep(1)
            response = session.get(url=image_url, headers=headers)

        with open(f'{directory}/{image_title}', 'wb') as file:
            file.write(response.content)

        print(f'Обработано изображений: {k}/{count_urls}')


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    cur_date = datetime.now().strftime('%d-%m-%Y')

    directory = 'results'

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = f'{directory}/result_data_{species}_{cur_date}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    try:
        # Считываем Excel-файл
        excel_data = read_excel('data/data.xlsx', sheet_name=0, header=None)  # sheet_name=0 для первой страницы

        # Преобразуем в список списков
        data_list = excel_data.values.tolist()

        # Собираем цены товаров
        result_data_price = get_products_price(products_urls_list=data_list, headers=headers)
        save_excel(data=result_data_price, species='price')

        # Собираем новые URL
        new_products_urls_list = get_products_urls(category_urls_list=category_urls_list, headers=headers)

        if new_products_urls_list:
            driver = init_chromedriver(headless_mode=True)
            try:
                print(f'Получено {len(new_products_urls_list)} новых товаров!')
                result_data_products = get_products_data(driver=driver, products_urls_list=new_products_urls_list)
            except Exception as ex:
                print(f'main: {ex}')
                result_data_products = None
            finally:
                driver.close()
                driver.quit()

            if result_data_products:
                save_excel(data=result_data_products, species='products')
                download_imgs(file_path="data/images_urls_list.txt", headers=headers)
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
