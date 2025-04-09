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
    "https://evroplast.ru/arochnyy-element/",
    "https://evroplast.ru/kaminy/",
    "https://evroplast.ru/dekorativnye-elementy/",
    "https://evroplast.ru/dopolnitelnye-elementy/",
    "https://evroplast.ru/karnizy/",
    "https://evroplast.ru/karnizy/gibkie/",
    "https://evroplast.ru/karnizy/?mat=pf,pps",
    "https://evroplast.ru/kessony-i-kupola/",
    "https://evroplast.ru/kolonny/",
    "https://evroplast.ru/kronshtejny/",
    "https://evroplast.ru/moldingi/",
    "https://evroplast.ru/moldingi/gibkie/",
    "https://evroplast.ru/moldingi/?mat=pf,pps",
    "https://evroplast.ru/obramlenie-arok/",
    "https://evroplast.ru/obramlenie-dverej/",
    "https://evroplast.ru/ornamenty/",
    "https://evroplast.ru/dekorativnii-paneli/",
    "https://evroplast.ru/potolochnye-paneli/",
    "https://evroplast.ru/piljastry/",
    "https://evroplast.ru/plintusy/",
    "https://evroplast.ru/plintusy/gibkie/",
    "https://evroplast.ru/plintusy/?mat=pf,pps",
    "https://evroplast.ru/polukolonny/",
    "https://evroplast.ru/rozetki/",
    "https://evroplast.ru/sandriki/",
    "https://evroplast.ru/sostavnye-elementy/",
    "https://evroplast.ru/uglovye-jelementy/",
    "https://evroplast.ru/elementy-kamina/",
    "https://evroplast.ru/karnizy-fasadnye/",
    "https://evroplast.ru/frizy/",
    "https://evroplast.ru/arhitravy-fasadnye/",
    "https://evroplast.ru/dopolnitelnye-elementy-fasadnye/",
    "https://evroplast.ru/piljastry-fasadnye/",
    "https://evroplast.ru/kolonny-fasadnye/",
    "https://evroplast.ru/polukolonny-fasadnye/",
    "https://evroplast.ru/baljasiny-dlya-balyustrad/",
    "https://evroplast.ru/stolby-dlya-balyustrad/",
    "https://evroplast.ru/kryshki-stolba-dlya-balyustrad/",
    "https://evroplast.ru/osnovaniya-dlya-balyustrad/",
    "https://evroplast.ru/poruchni-dlya-balyustrad/",
    "https://evroplast.ru/dopolnitelnye-elementy-dlya-balyustrad/",
    "https://evroplast.ru/montazhnyy-komplekt-dlya-balyustrad/",
    "https://evroplast.ru/nalichniki/",
    "https://evroplast.ru/arochnye-obramlenija/",
    "https://evroplast.ru/zamkovye-kamni/",
    "https://evroplast.ru/podokonnye-jelementy/",
    "https://evroplast.ru/dopolnitelnye-elementy-okonnye-obramlenija-fasad/",
    "https://evroplast.ru/kronshtejny-pedestaly/",
    "https://evroplast.ru/otkosy/",
    "https://evroplast.ru/nakladnye-elementy/",
    "https://evroplast.ru/sandriki-fasadnye/",
    "https://evroplast.ru/ornamenty-fasadnye/",
    "https://evroplast.ru/rusty/",
    "https://evroplast.ru/sostavnye-elementy-fasadnye/",
    "https://evroplast.ru/adhesive/",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}


# Функция инициализации объекта chromedriver
def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
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
        pages = int(soup.find('div', class_='pagination').find_all('a', class_='page-link')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


def get_products_urls(driver: Chrome, category_urls_list: list) -> list:
    count_urls = len(category_urls_list)

    new_products_urls_list = []
    processed_urls_set = set()

    with open('data/exceptions_urls_list.txt', 'r', encoding='utf-8') as file:
        exception_urls_list = [line.strip() for line in file]

    for i, category_url in enumerate(category_urls_list, 1):
        try:
            driver.get(url=category_url)
            time.sleep(1)
            html = driver.page_source

        except Exception as ex:
            print(f"{category_url} - {ex}")
            continue

        if not html:
            continue

        pages = get_pages(html=html)
        print(f'category_url: {category_url} pages: {pages}')

        for page in range(1, pages + 1):
            page_url = f"{category_url}?page={page}"
            try:
                driver.get(url=page_url)
                time.sleep(1)
                html = driver.page_source
            except Exception as ex:
                print(f"{page_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                data = soup.find('div', class_='cat-items').find_all('a')
                for item in data:
                    try:
                        product_url = f"https://evroplast.ru{item.get('href')}"
                    except Exception:
                        continue

                    if product_url in exception_urls_list or product_url in processed_urls_set:
                        continue
                    new_products_urls_list.append(product_url)
                    processed_urls_set.add(product_url)

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


def get_products_data(products_urls_list: list, headers: dict) -> list[dict]:
    count_urls = len(products_urls_list)
    result_data = []
    images_urls_list = []

    with Session() as session:
        for j, product_url in enumerate(products_urls_list, 1):
            product_images_urls_list = []
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
                category = soup.find('ul', itemprop='breadcrumb').find_all('li', itemprop='itemListElement')[
                    2].text.strip()
            except Exception:
                category = None

            try:
                data = soup.find('section', class_='prod-info-wrap')
            except Exception:
                continue

            try:
                title = data.find('h2', class_='product-title').text.strip()
            except Exception:
                title = None

            try:
                price = int(
                    ''.join(
                        filter(lambda x: x.isdigit(), soup.find('h2', class_='prod-info-price').text.strip()))) // 100
            except Exception:
                price = None

            try:
                type_option = data.find('a', class_='prod-info-type-option active').text.strip()
            except Exception:
                type_option = None

            try:
                images_items = soup.find('div', class_='sp-slides').find_all('img')
                for image_item in images_items:
                    image_url = f"https://evroplast.ru{image_item.get('src')}"
                    if image_url.lower().endswith(('.jpg', '.png', '.webp')):
                        images_urls_list.append(image_url)
                        product_images_urls_list.append(image_url)
                main_image_url = product_images_urls_list[0]
                additional_images_urls = '; '.join(product_images_urls_list[1:])
            except Exception:
                main_image_url = None
                additional_images_urls = None

            result_dict = {
                'Ссылка': product_url,
                'Категория': category,
                'Артикул': title,
                'Название товара': title,
                'Цена': price,
                'Тип': type_option,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
            }

            # Сбор параметров товара
            product_parameters = {}
            try:
                parameters_items = data.find('div', class_='prod-info-params-cont').find_all('div',
                                                                                             class_='prod-info-param-item')
                for parameter_item in parameters_items:
                    parameter_name = parameter_item.find('span', class_='prod-info-param-name').text.strip()
                    parameter_value = parameter_item.find('span', class_='prod-info-param-val').text.strip()
                    product_parameters[parameter_name] = parameter_value
            except Exception:
                pass

            result_dict.update(product_parameters)

            result_data.append(result_dict)

            print(f'Обработано товаров: {j}/{count_urls}')

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
                price = int(''.join(
                    filter(lambda x: x.isdigit(), soup.find('h2', class_='prod-info-price').text.strip()))) // 100
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
            if image_url.lower().endswith(('.jpg', '.png', '.webp')):
                time.sleep(1)
                response = session.get(url=image_url, headers=headers)
            else:
                continue

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

        driver = init_chromedriver(headless_mode=True)

        try:
            # Собираем новые URL
            new_products_urls_list = get_products_urls(driver=driver, category_urls_list=category_urls_list)
        except Exception as ex:
            print(f'main: {ex}')
            new_products_urls_list = None
        finally:
            driver.close()
            driver.quit()

        if new_products_urls_list:
            print(f'Получено {len(new_products_urls_list)} новых товаров!')
            result_data_products = get_products_data(products_urls_list=new_products_urls_list, headers=headers)
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
