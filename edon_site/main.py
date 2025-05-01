import os
import time
from datetime import datetime

from requests import Session

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter

start_time = datetime.now()

category_urls_list = [
    "https://edon.su/catalog/svarochnye_apparaty/",
    "https://edon.su/catalog/sredstva_zashchity/",
    "https://edon.su/catalog/generatory_elektrostantsii/",
    "https://edon.su/catalog/kompressornoe_oborudovanie/",
    "https://edon.su/catalog/stroitelnoe_oborudovanie/",
    "https://edon.su/catalog/gruzopodyemnoe_oborudovanie/",
    "https://edon.su/catalog/nasosnoe_oborudovanie/",
    "https://edon.su/catalog/podshipniki_1/",
    "https://edon.su/catalog/akkumulyatornyy_instrument/",
    "https://edon.su/catalog/nabory_akkumulyatornogo_instrumenta/",
    "https://edon.su/catalog/elektroinstrument_setevoy/",
    "https://edon.su/catalog/shurupoverty/",
    "https://edon.su/catalog/shlifovalnye_mashiny/",
    "https://edon.su/catalog/dreli_i_stroitelnye_miksery/",
    "https://edon.su/catalog/perforatory/",
    "https://edon.su/catalog/otboynye_molotki_1/",
    "https://edon.su/catalog/lobziki_i_sabelnye_pily/",
    "https://edon.su/catalog/pily_diskovye/",
    "https://edon.su/catalog/pily_tsepnye/",
    "https://edon.su/catalog/rubanki/",
    "https://edon.su/catalog/trimmery/",
    "https://edon.su/catalog/gaykoverty/",
    "https://edon.su/catalog/moyki_vysokogo_davleniya/",
    "https://edon.su/catalog/promyshlennye_pylesosy/",
    "https://edon.su/catalog/benzoinstrumenty/",
    "https://edon.su/catalog/otopitelnoe_oborudovanie/",
    "https://edon.su/catalog/opryskivateli/",
    "https://edon.su/catalog/pusko_zaryadnye_ustroystva/",
    "https://edon.su/catalog/stanki/",
    "https://edon.su/catalog/izmeritelnye_instrumenty/",
    "https://edon.su/catalog/okrasochnoe_oborudovanie/",
    "https://edon.su/catalog/pnevmoinstrument/",
    "https://edon.su/catalog/ruchnoy_instrument/",
    "https://edon.su/catalog/sistemy_filtratsii_solberg/",
    "https://edon.su/catalog/raskhodnye_materialy_i_osnastka_dlya_instrumenta/",
    "https://edon.su/catalog/zapchasti_servis_redbo_edon/",
    "https://edon.su/catalog/aktsionnye_tovary/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
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


# Получаем количество страниц
def get_pages(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('div', class_='module-pagination').find('div', class_='nums').find_all('a')[-1].text.strip())
    except Exception:
        pages = 1

    return pages


def get_products_urls(category_urls_list: list, headers: dict):
    category_count_urls = len(category_urls_list)

    products_urls_list = []
    processed_urls_set = set()

    with Session() as session:
        for i, category_url in enumerate(category_urls_list, 1):
            try:
                html = get_html(url=category_url, headers=headers, session=session)
            except Exception as ex:
                print(f"{category_url} - {ex}")
                continue
            pages = get_pages(html=html)

            for page in range(1, pages + 1):
                page_url = f"{category_url}?PAGEN_1={page}"
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
                    data = soup.find_all('div', class_='item-title')
                    for item in data:
                        try:
                            item_url = item.find('a').get('href')
                            product_url = f"https://edon.su{item_url}"
                        except Exception:
                            continue

                        if product_url in processed_urls_set:
                            continue

                        products_urls_list.append(product_url)
                        processed_urls_set.add(product_url)
                except Exception as ex:
                    print(f'{product_url}: {ex}')
                    continue

                print(f'Обработано страниц: {page}/{pages}')

            print(f'Обработано категорий: {i}/{category_count_urls}')

            directory = 'data'

            os.makedirs(directory, exist_ok=True)

            with open('data/products_urls_list.txt', 'a', encoding='utf-8') as file:
                print(*products_urls_list, file=file, sep='\n')

            products_urls_list.clear()


def get_products_data(file_path: str, headers: dict) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        products_urls_list = [line.strip() for line in file.readlines()]

    count_urls = len(products_urls_list)
    result_data = []

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
                elements_items = soup.find('div', id='navigation').find_all('span', itemprop='name')
            except Exception:
                continue

            try:
                category = elements_items[-3].text.strip()
            except Exception:
                category = None

            try:
                subcategory = elements_items[-2].text.strip()
            except Exception:
                subcategory = None

            try:
                product_name = elements_items[-1].text.strip()
            except Exception:
                product_name = None

            try:
                sku = soup.find('span', class_='article__value').text.strip()
            except Exception:
                sku = None

            try:
                price = ''.join(soup.find('div', class_='prices_block').find(
                    'span', class_="price_value").text.strip().replace('\xa0', ''))
            except Exception:
                price = None

            try:
                stock_status = soup.find('span', class_='store_view dotted').text.strip()
            except Exception:
                stock_status = None

            try:
                description = soup.find('div', class_='ordered-block__content').text.strip().replace('\xa0', '')

            except Exception:
                description = None

            try:
                images_items = soup.find_all('a', {'data-fancybox': 'gallery'})
                for image_item in images_items:
                    image_url = f"https://edon.su{image_item.get('href')}"
                    if image_url.lower().endswith(('.jpg', '.png', '.webp')):
                        product_images_urls_list.append(image_url)
                main_image_url = product_images_urls_list[0]
                additional_images_urls = '; '.join(product_images_urls_list[1:])
            except Exception:
                main_image_url = None
                additional_images_urls = None

            result_dict = {
                'Ссылка': product_url,
                'Категория': category,
                'Подкатегория': subcategory,
                'Название товара': product_name,
                'Артикул': sku,
                'Цена': price,
                'Наличие': stock_status,
                'Описание': description,
                'Главное изображение': main_image_url,
                'Дополнительные изображения': additional_images_urls,
            }

            # Сбор параметров товара
            product_parameters = {}
            try:
                properties_items = soup.find('div', class_='props_block').find_all('div', class_='properties-group__item')
                for prop_item in properties_items:
                    prop_group = prop_item.find('div', class_='properties-group__name-wrap').text.strip()
                    prop_value = prop_item.find('div', class_='properties-group__value-wrap').text.strip()
                    product_parameters[prop_group] = prop_value
            except Exception:
                pass

            result_dict.update(product_parameters)

            result_data.append(result_dict)

            print(f'Обработано товаров: {j}/{count_urls}')

    directory = 'data'

    os.makedirs(directory, exist_ok=True)

    return result_data


# Функция для записи данных в формат xlsx
def save_excel(data: list, species: str) -> None:
    directory = 'results'

    os.makedirs(directory, exist_ok=True)

    file_path = f'{directory}/result_data_{species}.xlsx'

    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='w') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    print(f'Данные сохранены в файл {file_path}')


def main():
    file_path_urls = "data/products_urls_list.txt"
    file_path_images = "data/images_urls_list.txt"

    try:
        # get_products_urls(category_urls_list=category_urls_list, headers=headers)
        result_data = get_products_data(file_path=file_path_urls, headers=headers)
        save_excel(data=result_data, species='products')
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
