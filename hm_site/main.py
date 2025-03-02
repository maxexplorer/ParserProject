import os
import re
import time
from datetime import datetime
from random import randint

from requests import Session

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pandas import DataFrame
from pandas import ExcelWriter
from pandas import read_excel

from data.data import category_data_list_tr
from data.data import colors_dict_de
from data.data import sizes_dict
from data.data import id_region_dict

from functions import translator
from functions import get_exchange_rate
from functions import get_unique_urls

start_time = datetime.now()

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': 'preshoppingUser=false; INGRESSCOOKIE=1727860329.262.73.100142|690fb80ac6d9f7009fc04fa34f769148; OptanonAlertBoxClosed=2024-10-02T09:12:14.591Z; utag_main_vapi_domain=hm.com; hmid=0BFE9A7D-77C6-4819-8AAD-48CA78B9C4D0; _fbp=fb.1.1727860335310.606249847180237751; _gcl_au=1.1.1661617167.1727860336; AMCVS_32B2238B555215F50A4C98A4%40AdobeOrg=1; _pin_unauth=dWlkPU56TXpPRE0yWW1VdE5UQmtPQzAwTVRWaExXSXdZV1l0TW1Rek56Z3hOakpqWldKbA; _ga=GA1.2.1950914713.1727860336; s_ecid=MCMID%7C28890392179810197603003150097585318351; agCookie=e26c8c81-f4f0-4aeb-9392-62417262ce08; hm-poland-cart=dc2b20f1-5ff8-4f5d-b4cb-36bdae9b9869; akavpau_www2_tr=1727961891~id=baf307bd878026802a9cbae4263f6f27; akavpau_www2_de_de=1728061975~id=c409bc6d4c0ead6040425f3aea6fa5e4; akainst=EU5; AKA_A2=A; _abck=9D5FE6D5EF5D843AE8C4A5AB80F54DFB~0~YAAQHCjdFw5zcyyTAQAAn0qmQwwLuiiVKNlshfP7aneVd0y2iHSIplPBEftTUTDUVK+MK6prIzOhBm+Ek4qTueZlOCSpj/7MUqlgzx/r9SlaLmiKLVvWUDdKy2GZSkTgz1BzZtfPanIh1QB6rR+goi0dB3W4Xp6ABc8vHkhw4hzrb/H9GV+jj5D4jVv0/fY1+36FobAx2VJ2I34kTJx9zfCVyPgJRNU6zPNwQmuBtRqmtg48RkRlgTJ0dAqxvlmkDQIflKaaewV41jPZE1chlJl7Ra84m8erUPjKsb4aTHQRH0K043ee9gECTHT8Y1ZsDtXHv/iKWuzcph96EVZZ0XbbE5Pe+oZZbK6RZJpEWBO+T3sVN2Ws1/bgOzQ3jX34SOQdVpLazVqtHvhxRIbEuNDjIdY5+wPP3CC1gCszAp4rifM7zWTAgj9kwJJPNFiU/T8QorbeZvyJqOZzEsXqBI63tCWEIqB82M/F2Q==~-1~-1~-1; bm_sz=153B84F408A915EA3878123E581044B1~YAAQHCjdFxFzcyyTAQAAn0qmQxn0Ytme8coNo1Ogel/lgwtA2xq9PpxdoqDQKcw2oh6QVZ73/fMENmqGK/ld8UGM+vCss6njV8FZG1wNCYtOCFyhx80L8rxdrLanAdhBZde40XBRX6baJtTDFHdal6X4ZYVdi9ZxhuIr/KKOHHrbJSbFTdhxN2Qyn3FZ422fx256CbRUSpnbME07krqiA6OqbygJbogLS6GsmP8tOKQLh6BZGbz36X87IClF8NMCwizL1XqIYxoKJ5M7uyccnSA4ZBh2iHJOe84SdbKGEof6TKj8Z/fxkOqmTPRKIrBI0lSvbPxSypiiAdge9JnGSK5QFTr7bcAyX+PeDjlS/XggNZBax5BPuQDAZuBPY3lQk/4+xwsKXlc/~3490371~4405559; JSESSIONID=4FFE53AAA1492E09DF6FCE2E3800176FAB9C1F0723BBE559ABC2A8091A9B8A65623EB17F82F45CD51BD7B73DABD2575099B3379A090AFEB4B5F487C4FC091312.hybris-ecm-web-678cccbdf6-dfwlq; utag_main__sn=25; utag_main_ses_id=1732006795368%3Bexp-session; utag_main__pn=1%3Bexp-session; dep_sid=s_7158716817278081.1732006795373; utag_main_segment=normal%3Bexp-session; utag_main__ss=0%3Bexp-session; ak_bmsc=3343BEEDBFC0D27FBBA14DF269D46EFF~000000000000000000000000000000~YAAQHCjdF0J4cyyTAQAAxVimQxkbstjfmtaaeaPVLlEEt7ycZRpDSm4pP69moOwdPmXXxLcm2FezuRBvjdUI81d00vb8jR7+Mpa+bAQMXchJsEvloJETv82c+wijrda5WplC8E4Bv9W+cypgBCBIlhT99EP3WvNQUN1mmriEpnEl/WmAE1r9wCPWGop9XWb49/uqTKsifcAvmEsZGqr7HFpxJeA0f/SPbKYOZMnvcAZ7zxfPtPfESg81rZZ+5pImIzuvv+gSn/EYuKxVABJbstP3jW/WGq5OV5BuRmeXM3KDbf1FeFI69eiQ+5OXLdQ4p7rzEX99eZDg52x/zri3PVt5aTZDIr8H5lV8oayhHiivFlJr7uz5vteSquWq7EKfZHD0jgrE9JS8XUOhx2Q2ZjT4Z0jkA1tRWf247FXsqQWB3vsskJZLqWBJMGsIabnvdmueeN3U/g==; _uetsid=a60a5930a65411ef96d679d7daddef26; _uetvid=6b2c92a0809e11efa813ed1bec30d9d5; utag_main__se=4%3Bexp-session; utag_main__st=1732008596637%3Bexp-session; dep_exp=Tue, 19 Nov 2024 09:29:56 GMT; AMCV_32B2238B555215F50A4C98A4%40AdobeOrg=179643557%7CMCIDTS%7C20047%7CMCMID%7C28890392179810197603003150097585318351%7CMCAAMLH-1732611596%7C6%7CMCAAMB-1732611596%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1732013996s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C2008772682%7CvVersion%7C5.5.0; _ga_Z1370GPB5L=GS1.2.1732006796.29.0.1732006796.60.0.0; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Nov+19+2024+11%3A59%3A57+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202401.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=324134e5-3c0d-4304-94d9-d1e137bbd05c&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=RU%3BMOW&AwaitingReconsent=false; userCookie=##eyJjYXJ0Q291bnQiOjB9##; akamref=pl_pl; akavpau_www2_pl_pl=1732007102~id=c6a259f5d6d5738133e2c91c03e732e8; bm_sv=80B0C8AC7E676D5F05ACFE4FE7A0E167~YAAQHCjdF2qAcyyTAQAAAHOmQxkgacwS8C5AILnCMQtIa2Kzb8pjumfgLOHAkHgLKYDYaOax2P0Ff33O72JQnvouUviriTfQA6xbAAc/hvBEFRotZZdsa3R1dLrWXXL1UPF7KrfjjzCFFXi8W4YuvChTFdCt7/1TgIRk2Tx5vSfml1yEha/Jx4F11apxC0+JM0mXGfyDyOwkNdNbF4PqDiDyHVqndmtE5PaPQoX7fsIHU0K09aVmRb0zCc0=~1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}


# Функция инициализации объекта chromedriver
def init_chromedriver(headless_mode: bool = False) -> Chrome:
    options = Options()
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
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
            raise Exception(f'status_code: {response.status_code}')

        html = response.text
        return html
    except Exception as ex:
        print(f'get_html: {ex}')


# Получаем количество страниц
def get_pages_de(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-label': 'Paginierung'}).find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Получаем количество страниц
def get_pages_pl(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(
            soup.find('nav', {'aria-labelledby': 'pagination-accessibility-label'}).find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Получаем количество страниц
def get_pages_tr(html: str) -> int:
    soup = BeautifulSoup(html, 'lxml')

    try:
        pages = int(soup.find('nav', {'aria-labelledby': 'pagination-accessibility-label'}).find_all('li')[-2].text.strip())
    except Exception:
        pages = 1

    return pages


# Функция получения количества страниц
def get_category_urls(driver: Chrome, region: str, id_region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/category_data_list_{region}.txt'

    category_data_list = []

    url = f"https://www2.hm.com/{id_region}/index.html"

    driver.get(url=url)
    html = driver.page_source

    soup = BeautifulSoup(html, 'lxml')

    try:
        # data = soup.find('ul', class_='MLEL').find_all('li')
        data = soup.find_all('li', {'data-level': "3"})

        for item in data:
            category_name = item.text
            try:
                category_url = f"https://www2.hm.com{item.find('a').get('href')}"
            except Exception as ex:
                print(f' category_url: {ex}')
                continue

            category_data_list.append(
                (category_name, category_url)
            )

    except Exception as ex:
        print(f':get_category_urls: {ex}')

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', encoding='utf-8') as file:
        print(*category_data_list, file=file, sep='\n')


# Функция получения ссылок товаров
def get_products_urls(driver: Chrome, headers: dict, category_data_list: list, brand: str,
                      region: str) -> None:
    # Путь к файлу для сохранения URL продуктов
    directory = 'data'
    file_path = f'{directory}/url_products_list_{brand}_{region}.txt'

    try:
        processed_urls = get_unique_urls(file_path=file_path)
    except FileNotFoundError:
        processed_urls = set()

    with Session() as session:
        for category_dict in category_data_list:
            for category_name, category_list in category_dict.items():
                for product_tuple in category_list:
                    products_data_list = []
                    products_urls = []
                    subcategory_name, category_url = product_tuple

                    try:
                        time.sleep(1)
                        html = get_html(url=category_url, headers=headers, session=session)
                    except Exception as ex:
                        print(f"{category_url} - {ex}")
                        continue

                    if region == 'Германия':
                        pages = get_pages_de(html=html)
                    elif region == 'Турция':
                        pages = get_pages_tr(html=html)
                    elif region == 'Польша':
                        pages = get_pages_pl(html=html)
                    else:
                        pages = get_pages_de(html=html)

                    print(f'В категории {category_name}/{subcategory_name}: {pages} страниц')

                    for page in range(1, pages + 1):
                        page_product_url = f"{category_url}?page={page}"
                        try:
                            time.sleep(1)
                            html = get_html(url=page_product_url, headers=headers, session=session)
                        except Exception as ex:
                            print(f"{page_product_url} - {ex}")
                            continue

                        if not html:
                            continue

                        soup = BeautifulSoup(html, 'lxml')

                        try:
                            product_items = soup.find('ul', {'data-elid': 'product-grid'}).find_all('div',
                                                                                                    class_='a4d8ee')
                            for product_item in product_items:
                                try:
                                    product_url = product_item.find('a').get('href')
                                except Exception as ex:
                                    print(ex)
                                    continue
                                products_urls.append(product_url)
                        except Exception as ex:
                            print(ex)

                        print(f'Обработано: {page}/{pages} страниц')

                        # Проверяем кратность 10 или достижение последней страницы
                        if page % 10 == 0 or page == pages:
                            products_data_list.append(
                                {
                                    (category_name, subcategory_name): products_urls
                                }
                            )

                            if region == 'Германия':
                                get_products_data(driver=driver, products_data_list=products_data_list,
                                                  processed_urls=processed_urls,
                                                  brand=brand, region=region, size_model_title='Größe des Models')
                            elif region == 'Турция':
                                get_products_data(driver=driver, products_data_list=products_data_list,
                                                  processed_urls=processed_urls,
                                                  brand=brand, region=region, size_model_title='Model bedeni')
                            elif region == 'Польша':
                                get_products_data(driver=driver, products_data_list=products_data_list,
                                                  processed_urls=processed_urls,
                                                  brand=brand, region=region, size_model_title='Rozmiar modela/modelki')

                            if not os.path.exists(directory):
                                os.makedirs(directory)

                            with open(file_path, 'a', encoding='utf-8') as file:
                                print(*products_urls, file=file, sep='\n')

                            products_urls.clear()  # Очищаем список после обработки
                            products_data_list.clear()  # Очищаем накопленные данные


# Функция получения данных товаров
def get_products_data(driver: Chrome, products_data_list: list[dict], processed_urls: set, brand: str,
                      region: str, size_model_title: str) -> None:

    count = 0

    for dict_item in products_data_list:
        result_data = []
        product_urls = []
        key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

        for product_url in values:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                product_urls.append(product_url)
        category_name = key[0]
        subcategory_name = key[1]

        count_products = len(product_urls)
        print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')

        for i, product_url in enumerate(product_urls, 1):
            try:
                driver.get(url=product_url)
                driver.execute_script("window.scrollTo(0, 2000);")
                time.sleep(1)
                # driver.execute_script("window.scrollTo(0, 4000);")
                # time.sleep(1)
                html = driver.page_source
            except Exception as ex:
                print(f"{product_url} - {ex}")
                count += 1

                if count > 5:
                    raise ex
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                id_product = product_url.split('.')[-2]
            except Exception:
                id_product = None

            try:
                data = soup.find('div', class_='rOGz')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                name = data.find('h1').text.strip()
                product_name = f'H&M {name.lower()}'
                product_name_rus = f'H&M {translator(name).lower()}'
            except Exception:
                product_name = None
                product_name_rus = None

            try:
                price = int(''.join(
                    i for i in data.find('span', class_='edbe20 ac3d9e d9ca8b').text.split()[0] if
                    i.isdigit())) / 100
            except Exception:
                price = None

            old_price = None

            if not price:
                try:
                    old_price = int(''.join(
                        i for i in data.find('span', class_='e98f30 ac3d9e e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    old_price = None

                try:
                    price = int(''.join(
                        i for i in data.find('span', class_='edbe20 ac3d9e c8e3aa e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    price = None

            try:
                color_original = None
                color_items = data.find('div', {'data-testid': 'grid', 'aria-live': 'polite'}).find_all('a')
                for color_item in color_items:
                    if color_item.get('aria-checked') == 'true':
                        color_original = color_item.get('title').lower()
                if region == 'Германия':
                    color_rus = colors_dict_de.get(color_original, color_original).lower()
                else:
                    color_rus = translator(color_original)
            except Exception as ex:
                print(f'color: {product_url} - {ex}')
                color_original = None
                color_rus = None

            try:
                images_urls_list = []
                images_items = data.find('ul', {'data-testid': 'grid-gallery'}).find_all('li')
                for item in images_items:
                    image_url = item.find('img').get('src')
                    image_url = image_url.split('?')[0]
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception as ex:
                print(f'images: {product_url} - {ex}')
                main_image_url = None
                additional_images_urls = None

            try:
                if category_name == 'Женщины':
                    gender = 'женский'
                elif category_name == 'Мужчины':
                    gender = 'мужской'
                else:
                    gender = category_name
            except Exception:
                gender = None

            try:
                section_description = data.find('div', id='section-descriptionAccordion')
            except Exception:
                section_description = None

            try:
                description = section_description.find('p').text.strip()
                description_rus = translator(description)
            except Exception:
                description = None
                description_rus = None

            model_height = None
            model_size = None

            try:
                model_size_description = section_description.find('dl').find(
                    string=re.compile(size_model_title)).find_next().text.split('cm')
            except Exception:
                model_size_description = None

            if model_size_description:
                try:
                    model_height = model_size_description[0].split()[-1]
                except Exception:
                    model_height = None

                try:
                    model_size = model_size_description[-1].split()[-1].replace('.', '').replace(')', '')
                except Exception:
                    model_size = None

            try:
                section_material_description = data.find('div', id='section-materialsAndSuppliersAccordion')
            except Exception:
                section_material_description = None

            try:
                composition_outer_shell = section_material_description.find('li').text
                composition = translator(composition_outer_shell)
                material_outer_shell = composition_outer_shell.split()[0]
                material = translator(material_outer_shell)
            except Exception:
                composition = None
                material = None

            try:
                section_care = data.find('div', id='section-careGuideAccordion').find('ul').find_all('li')
            except Exception:
                section_care = None

            try:
                care = '. '.join(i.text for i in section_care)
                care = translator(care)
            except Exception:
                care = None

            try:
                sizes_items = data.find('div', {'data-testid': 'size-selector'}).find_all('li')
            except Exception:
                sizes_items = None

            try:
                sizes = data.find('div', {'data-testid': 'size_list_name'}).text.strip()
            except Exception:
                sizes = None

            if not sizes_items:
                sizes_items = ' '

            for size_item in sizes_items:
                try:
                    size_eur = size_item.find('input').get('id')
                except Exception:
                    size_eur = ''

                try:
                    size_availability = size_item.find('label').find('span').text.strip()
                except Exception:
                    size_availability = None

                if not size_availability:
                    status_size = 'в наличии'
                else:
                    status_size = translator(size_availability).lower()

                try:
                    size_rus = sizes_dict[category_name][size_eur]
                except Exception:
                    size_rus = size_eur

                if not size_eur:
                    size_eur = sizes
                    size_rus = translator(sizes)

                id_product_size = f"{id_product}/{size_eur}"

                result_data.append(
                    {
                        '№': product_name,
                        'Артикул': id_product_size,
                        'Название товара': product_name_rus,
                        'Цена, руб.*': price,
                        'Цена до скидки, руб.': old_price,
                        'НДС, %*': None,
                        'Включить продвижение': None,
                        'Ozon ID': id_product_size,
                        'Штрихкод (Серийный номер / EAN)': None,
                        'Вес в упаковке, г*': None,
                        'Ширина упаковки, мм*': None,
                        'Высота упаковки, мм*': None,
                        'Длина упаковки, мм*': None,
                        'Ссылка на главное фото*': main_image_url,
                        'Ссылки на дополнительные фото': additional_images_urls,
                        'Ссылки на фото 360': None,
                        'Артикул фото': None,
                        'Бренд в одежде и обуви*': brand,
                        'Объединить на одной карточке*': id_product,
                        'Цвет товара*': color_rus,
                        'Российский размер*': size_rus,
                        'Размер производителя': size_eur,
                        'Статус наличия': status_size,
                        'Название цвета': color_original,
                        'Тип*': category_name,
                        'Пол*': subcategory_name,
                        'Размер пеленки': None,
                        'ТН ВЭД коды ЕАЭС': None,
                        'Ключевые слова': None,
                        'Сезон': None,
                        'Рост модели на фото': model_height,
                        'Параметры модели на фото': None,
                        'Размер товара на фото': model_size,
                        'Коллекция': None,
                        'Страна-изготовитель': None,
                        'Вид принта': description,
                        'Аннотация': description_rus,
                        'Инструкция по уходу': care,
                        'Серия в одежде и обуви': None,
                        'Материал': material,
                        'Состав материала': composition,
                        'Материал подклада/внутренней отделки': None,
                        'Материал наполнителя': None,
                        'Утеплитель, гр': None,
                        'Диапазон температур, °С': None,
                        'Стиль': None,
                        'Вид спорта': None,
                        'Вид одежды': None,
                        'Тип застежки': None,
                        'Длина рукава': None,
                        'Талия': None,
                        'Для беременных или новорожденных': None,
                        'Тип упаковки одежды': None,
                        'Количество в упаковке': None,
                        'Состав комплекта': None,
                        'Рост': None,
                        'Длина изделия, см': None,
                        'Длина подола': None,
                        'Форма воротника/горловины': None,
                        'Детали': None,
                        'Таблица размеров JSON': None,
                        'Rich-контент JSON': None,
                        'Плотность, DEN': None,
                        'Количество пар в упаковке': None,
                        'Класс компрессии': None,
                        'Персонаж': None,
                        'Праздник': None,
                        'Тематика карнавальных костюмов': None,
                        'Признак 18+': None,
                        'Назначение спецодежды': None,
                        'HS-код': None,
                        'Количество заводских упаковок': None,
                        'Ошибка': None,
                        'Предупреждение': None,
                    }
                )


            print(f'Обработано: {i}/{count_products} товаров!')

        if result_data:
            save_excel(data=result_data, brand=brand, category_name=category_name, region=region)


# Функция получения данных товаров
def get_products_data1(driver: Chrome, products_data_list: list[dict], processed_urls: set, brand: str,
                       region: str, size_model_title: str) -> None:
    result_data = []

    count = 0

    for dict_item in products_data_list:
        product_urls = []
        key, values = list(dict_item.keys())[0], list(dict_item.values())[0]

        for product_url in values:
            if product_url not in processed_urls:
                processed_urls.add(product_url)
                product_urls.append(product_url)
        category_name = key[0]
        subcategory_name = key[1]

        count_products = len(product_urls)
        print(f'В категории: {category_name}/{subcategory_name} - {count_products} товаров!')

        for i, product_url in enumerate(product_urls, 1):
            try:
                driver.get(url=product_url)
                driver.execute_script("window.scrollTo(0, 2000);")
                time.sleep(1)
                # driver.execute_script("window.scrollTo(0, 4000);")
                # time.sleep(1)
                html = driver.page_source
            except Exception as ex:
                print(f"{product_url} - {ex}")
                count += 1

                if count > 5:
                    raise ex
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')

            try:
                id_product = product_url.split('.')[-2]
            except Exception:
                id_product = None

            try:
                data = soup.find('div', class_='product parbase')
            except Exception as ex:
                print(f'data: {product_url} - {ex}')
                continue

            try:
                name = data.find('h1').text.strip()
                product_name = f'H&M {translator(name).lower()}'
            except Exception:
                product_name = None

            try:
                price = int(''.join(
                    i for i in data.find('span', class_='edbe20 ac3d9e d9ca8b e29fbf').text.split()[0] if
                    i.isdigit())) / 100
            except Exception:
                price = None

            old_price = None

            if not price:
                try:
                    old_price = int(''.join(
                        i for i in data.find('span', class_='e98f30 ac3d9e e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    old_price = None

                try:
                    price = int(''.join(
                        i for i in data.find('span', class_='edbe20 ac3d9e c8e3aa e29fbf').text.split()[0] if
                        i.isdigit())) / 100
                except Exception:
                    price = None

            try:
                color_original = data.find('h3', class_='product-input-label').text.strip().lower()
            except Exception:
                color_original = None

            try:
                images_urls_list = []
                images_items = data.find('div', class_='sticky-candidate').find_all('figure')
                for item in images_items:
                    image_url = f"https:{item.find('img').get('src')}"
                    images_urls_list.append(image_url)
                main_image_url = images_urls_list[0]
                additional_images_urls = '; '.join(images_urls_list)
            except Exception:
                print('not images')
                main_image_url = None
                additional_images_urls = None

            try:
                if category_name == 'Женщины':
                    gender = 'женский'
                elif category_name == 'Мужчины':
                    gender = 'мужской'
                else:
                    gender = category_name
            except Exception:
                gender = None

            try:
                section_description = data.find('div', id='section-descriptionAccordion')
            except Exception:
                section_description = None

            try:
                description = section_description.find('p').text.strip()
                description = translator(description)
            except Exception:
                description = None

            model_height = None
            model_size = None

            try:
                model_size_description = section_description.find('dl').find(
                    string=re.compile(size_model_title)).find_next().text.split('cm')
            except Exception:
                model_size_description = None

            if model_size_description:
                try:
                    model_height = model_size_description[0].split()[-1]
                except Exception:
                    model_height = None

                try:
                    model_size = model_size_description[-1].split()[-1].replace('.', '').replace(')', '')
                except Exception:
                    model_size = None

            try:
                section_material_description = data.find('div', id='section-materialsAndSuppliersAccordion')
            except Exception:
                section_material_description = None

            try:
                composition_outer_shell = section_material_description.find('li').find('p').text
                composition = translator(composition_outer_shell)
                material_outer_shell = composition_outer_shell.split()[0]
                material = translator(material_outer_shell)
            except Exception:
                composition = None
                material = None

            try:
                section_care = data.find('div', id='section-careGuideAccordion').find('ul').find_all('li')
            except Exception:
                section_care = None

            try:
                care = '. '.join(i.text for i in section_care)
                care = translator(care)
            except Exception:
                care = None

            try:
                sizes_items = data.find('hm-size-selector', class_='size-selector').find_all('li')

                for size_item in sizes_items:
                    size_eur = size_item.find('input').get('id')
                    try:
                        size_availability = size_item.find('input', {'type': 'radio'}).has_attr('disabled')
                    except Exception:
                        size_availability = None

                    if not size_availability:
                        status_size = 'в наличии'
                    else:
                        status_size = 'нет в наличии'

                    try:
                        size_rus = sizes_dict[category_name][size_eur]
                    except Exception:
                        size_rus = size_eur

                    id_product_size = f"{id_product}/{size_eur}"

                    result_data.append(
                        {
                            '№': None,
                            'Артикул': id_product_size,
                            'Название товара': product_name,
                            'Цена, руб.*': price,
                            'Цена до скидки, руб.': old_price,
                            'НДС, %*': None,
                            'Включить продвижение': None,
                            'Ozon ID': id_product_size,
                            'Штрихкод (Серийный номер / EAN)': None,
                            'Вес в упаковке, г*': None,
                            'Ширина упаковки, мм*': None,
                            'Высота упаковки, мм*': None,
                            'Длина упаковки, мм*': None,
                            'Ссылка на главное фото*': main_image_url,
                            'Ссылки на дополнительные фото': additional_images_urls,
                            'Ссылки на фото 360': None,
                            'Артикул фото': None,
                            'Бренд в одежде и обуви*': brand,
                            'Объединить на одной карточке*': id_product,
                            'Цвет товара*': color_original,
                            'Российский размер*': size_rus,
                            'Размер производителя': size_eur,
                            'Статус наличия': status_size,
                            'Название цвета': color_original,
                            'Тип*': subcategory_name,
                            'Пол*': gender,
                            'Размер пеленки': None,
                            'ТН ВЭД коды ЕАЭС': None,
                            'Ключевые слова': None,
                            'Сезон': None,
                            'Рост модели на фото': model_height,
                            'Параметры модели на фото': None,
                            'Размер товара на фото': model_size,
                            'Коллекция': None,
                            'Страна-изготовитель': None,
                            'Вид принта': None,
                            'Аннотация': description,
                            'Инструкция по уходу': care,
                            'Серия в одежде и обуви': None,
                            'Материал': material,
                            'Состав материала': composition,
                            'Материал подклада/внутренней отделки': None,
                            'Материал наполнителя': None,
                            'Утеплитель, гр': None,
                            'Диапазон температур, °С': None,
                            'Стиль': None,
                            'Вид спорта': None,
                            'Вид одежды': None,
                            'Тип застежки': None,
                            'Длина рукава': None,
                            'Талия': None,
                            'Для беременных или новорожденных': None,
                            'Тип упаковки одежды': None,
                            'Количество в упаковке': None,
                            'Состав комплекта': None,
                            'Рост': None,
                            'Длина изделия, см': None,
                            'Длина подола': None,
                            'Форма воротника/горловины': None,
                            'Детали': None,
                            'Таблица размеров JSON': None,
                            'Rich-контент JSON': None,
                            'Плотность, DEN': None,
                            'Количество пар в упаковке': None,
                            'Класс компрессии': None,
                            'Персонаж': None,
                            'Праздник': None,
                            'Тематика карнавальных костюмов': None,
                            'Признак 18+': None,
                            'Назначение спецодежды': None,
                            'HS-код': None,
                            'Количество заводских упаковок': None,
                            'Ошибка': None,
                            'Предупреждение': None,
                        }
                    )
            except Exception as ex:
                print(f'sizes: {product_url} - {ex}')

            print(f'Обработано: {i}/{count_products} товаров!')

        save_excel(data=result_data, brand=brand, category_name=category_name, region=region)


# Функция для записи данных в формат xlsx
def save_excel(data: list, brand: str, category_name: str, region: str) -> None:
    directory = 'results'

    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Путь к файлу для сохранения данных
    file_path = f'{directory}/result_data_{brand}_{category_name}_{region}.xlsx'

    # Если файл не существует, создаем его с пустым DataFrame
    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name='ОЗОН', index=False)

    # Загружаем данные из файла
    df = read_excel(file_path, sheet_name='ОЗОН')

    # Определение количества уже записанных строк
    num_existing_rows = len(df.index)

    # Добавляем новые данные
    dataframe = DataFrame(data)

    with ExcelWriter(file_path, mode='a',
                     if_sheet_exists='overlay') as writer:
        dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='ОЗОН',
                           index=False)

    print(f'Данные сохранены в файл "{file_path}"')


def main():
    driver = init_chromedriver(headless_mode=True)

    brand = 'H&M'

    value = input('Введите значение:\n1 - Германия\n2 - Турция\n3 - Польша\n')

    try:
        if value == '1':
            region = 'Германия'
            base_currency = 'EUR'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс EUR/RUB: {currency}')

            get_products_urls(driver=driver, headers=headers, category_data_list=[],
                              brand=brand, region=region)
        elif value == '2':
            region = 'Турция'
            base_currency = 'TRY'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс TRY/RUB: {currency}')

            get_products_urls(driver=driver, headers=headers, category_data_list=category_data_list_tr,
                              brand=brand, region=region)

            # id_region = id_region_dict.get(region)
            # get_category_urls(driver=driver, region=region, id_region=id_region)
        elif value == '3':
            region = 'Польша'
            base_currency = 'PLN'
            target_currency = 'RUB'
            currency = get_exchange_rate(base_currency=base_currency, target_currency=target_currency)
            print(f'Курс PLN/RUB: {currency}')

            get_products_urls(driver=driver, headers=headers, category_data_list=[],
                              brand=brand, region=region)
        else:
            raise ValueError('Введено неправильное значение')
    except Exception as ex:
        print(f'main: {ex}')
        input("Нажмите Enter, чтобы закрыть программу...")
    finally:
        driver.close()
        driver.quit()

    execution_time = datetime.now() - start_time
    print('Сбор данных завершен!')
    print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    main()
