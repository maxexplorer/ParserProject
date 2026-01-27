# parser.py
import time, os, re
from datetime import datetime
from requests import Session
from pandas import DataFrame, ExcelWriter, read_excel

from new_undetected_chromedriver import Chrome as undetectedChrome
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from image_processor import process_image
from config import IMAGE_DIR, USE_IMAGE_PROCESSING, CROP, IMAGE_QUALITY

from image_upload_client import ImageUploader


# --- Инициализация драйвера ---
def init_undetected_chromedriver(headless_mode=False, page_load_timeout=10):
    if headless_mode:
        options = ChromeOptions()
        options.add_argument('--headless')
        driver = undetectedChrome(options=options)
        driver.implicitly_wait(page_load_timeout)
    else:
        driver = undetectedChrome()
        driver.maximize_window()
        driver.implicitly_wait(page_load_timeout)
    return driver


# --- Сбор ссылок на товары ---
def get_products_urls(driver: undetectedChrome, pages: int = 315, file_path: str = 'data/product_urls_list.txt'):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    for page in range(1, pages + 1):
        products_urls = []
        page_url = f"https://www.ozon.ru/category/avtomagnitoly-8742/mediabass-101025819/?page={page}"

        try:
            driver.get(page_url)
            time.sleep(3)
            html = driver.page_source
        except Exception as ex:
            print(f"{page_url} - {ex}")
            continue

        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')
        try:
            data_items = soup.find('div', {'data-widget': 'tileGridDesktop'}).find_all('div',
                                                                                       class_='tile-root ji0_24 pi5_24 pi6_24')
        except Exception as ex:
            print(f'data_items: {page_url} - {ex}')
            continue

        for item in data_items:
            try:
                product_url = f"https://www.ozon.ru{item.find('a').get('href')}"
            except Exception:
                product_url = ''
            products_urls.append(product_url)

        print(f'Обработано: {page}/{pages} страниц')
        with open(file_path, 'a', encoding='utf-8') as f:
            print(*products_urls, file=f, sep='\n')


# --- Убираем дубликаты URL ---
def get_unique_urls(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        unique_urls = set(line.strip() for line in f)
    with open(file_path, 'w', encoding='utf-8') as f:
        print(*unique_urls, file=f, sep='\n')


def scroll_and_wait_description(driver, timeout=10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    wait = WebDriverWait(driver, timeout)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#section-description')))
    except:
        pass

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#section-characteristics')))
    except:
        pass


# --- Сохранение в Excel ---
def save_excel(data: list[dict], brand: str, sheet_name: str = 'Лист1'):
    cur_date = datetime.now().strftime('%d-%m-%Y')
    directory = 'results'
    os.makedirs(directory, exist_ok=True)
    file_path = f'{directory}/result_data_{brand}_{cur_date}.xlsx'

    if not os.path.exists(file_path):
        with ExcelWriter(file_path, mode='w') as writer:
            DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    df_existing = read_excel(file_path, sheet_name=sheet_name)
    num_existing_rows = len(df_existing.index)

    new_df = DataFrame(data)
    with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
        new_df.to_excel(writer, startrow=num_existing_rows, header=(num_existing_rows == 0), sheet_name=sheet_name,
                        index=False)

    print(f'Сохранено {len(data)} записей в {file_path}')


# --- Сбор данных о товарах + обработка/загрузка изображений ---
def get_products_data(driver: undetectedChrome, product_urls_list: list, brand: str):
    result_list = []
    batch_size = 100
    session = Session()
    # --- инициализация клиента загрузки ---
    image_client = ImageUploader()

    for i, product_url in enumerate(product_urls_list[1500:2100], 1500):
        try:
            driver.get(product_url)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-widget="webProductHeading"]')))
            scroll_and_wait_description(driver)
            html = driver.page_source
        except:
            continue

        soup = BeautifulSoup(html, 'lxml')

        if not soup.find('div', {'data-widget': 'webProductHeading'}):
            continue

        try:
            category = soup.find('div', {'data-widget': 'breadCrumbs'}).find_all('li')[-2].text.strip()
        except Exception:
            category = None

        try:
            name = soup.find('div', {'data-widget': 'webProductHeading'}).find('h1').text.strip()
        except Exception:
            name = None

        try:
            article = ''.join(
                filter(lambda x: x.isdigit(), soup.find('button', {'data-widget': 'webDetailSKU'}).text.strip()))
        except Exception:
            article = None

        try:
            price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', string=re.compile(
                'без Ozon Банка')).find_parent().find_parent().find('span').text))
        except Exception:
            price = None

        try:
            discount_price = ''.join(filter(lambda x: x.isdigit(), soup.find('span', string=re.compile(
                'c Ozon Банком')).find_parent().text))
        except Exception:
            discount_price = None

        if not price:
            continue

        # --- Изображения ---
        images_urls_list = []
        first_image_url = None

        try:
            images_items = soup.find('div', {'data-widget': 'webGallery'}).find_all('div', class_='pdp_ae3')

            for image_item in images_items:
                try:
                    image_url = image_item.find('img').get('src')
                    image_url = re.sub(r'wc\d+', 'wc1000', image_url)
                except Exception:
                    continue

                if USE_IMAGE_PROCESSING:
                    local_path = process_image(image_url, session, IMAGE_DIR, crop=CROP, quality=IMAGE_QUALITY)
                    if local_path:
                        uploaded_path = image_client.upload(local_path)
                        if uploaded_path:
                            first_image_url = uploaded_path
                            break  # нашли первую рабочую ссылку, выходим
                else:
                    images_urls_list.append(image_url)

        except Exception:
            pass

        # Получаем итоговую ссылку или список
        if USE_IMAGE_PROCESSING:
            images_urls = first_image_url
        else:
            images_urls = ' | '.join(images_urls_list) if images_urls_list else None

        # --- Описание ---
        description = ''
        for d in soup.find_all('div', id='section-description'):
            try:
                description += d.find('div', class_='RA-a1').text.strip()
            except:
                continue
        description = description or None

        # --- Характеристики в отдельные колонки ---
        item_characteristics = {}
        char_section = soup.find('div', id='section-characteristics')
        if char_section:
            for dl in char_section.find_all('dl'):
                try:
                    key = dl.find('dt').text.strip()
                    value = dl.find('dd').text.strip()
                    item_characteristics[key] = value
                except:
                    continue

        # --- Сохраняем результат ---
        result_item = {
            'Бренд': brand,
            'Категория': category,
            'Название': name,
            'Артикул': article,
            'Цена без Ozon Карты': price,
            'Цена c Ozon Картой': discount_price,
            'Ссылка на изображения': images_urls,
            'Описание': description
        }

        # Добавляем характеристики как отдельные колонки
        result_item.update(item_characteristics)

        result_list.append(result_item)

        print(f'Обработано: {i}/{len(product_urls_list)}')

        if len(result_list) >= batch_size:
            save_excel(result_list, brand)
            result_list.clear()

    if result_list:
        save_excel(result_list, brand)
