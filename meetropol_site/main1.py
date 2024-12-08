import os
import time
from datetime import datetime
from random import randint
from requests import Session
from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter, read_excel
from data.data import category_urls_list

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}


class ProductScraper:
    def __init__(self, headers, category_urls_list):
        self.headers = headers
        self.category_urls_list = category_urls_list
        self.processed_urls = set()
        self.start_time = datetime.now()

    def get_html(self, url: str, session: Session) -> str:
        """Получаем html разметку страницы"""
        try:
            response = session.get(url=url, headers=self.headers, timeout=60)
            if response.status_code != 200:
                print(f'status_code: {response.status_code}')
            return response.text
        except Exception as ex:
            print(f'get_html: {ex}')
            return ""

    def get_pages(self, html: str) -> int:
        """Получаем количество страниц"""
        soup = BeautifulSoup(html, 'lxml')
        try:
            pages = int(soup.find('div', class_='catalog-pagination d-flex').find_all('li')[-1].find('a').get('href').split('=')[-1])
        except Exception:
            pages = 1
        return pages

    def get_products_urls(self):
        """Получаем ссылки на товары"""
        with Session() as session:
            for category_url in self.category_urls_list:
                products_urls = []
                print(f'Обрабатывается ссылка: {category_url}')
                try:
                    time.sleep(randint(1, 3))
                    html = self.get_html(url=category_url, session=session)
                except Exception as ex:
                    print(f"{category_url} - {ex}")
                    continue

                pages = self.get_pages(html)
                for page in range(1, pages + 1):
                    category_page_url = f"{category_url}?PAGEN_1={page}"
                    try:
                        time.sleep(randint(1, 3))
                        html = self.get_html(url=category_page_url, session=session)
                    except Exception as ex:
                        print(f"{category_page_url} - {ex}")
                        continue

                    if not html:
                        continue

                    soup = BeautifulSoup(html, 'lxml')
                    try:
                        product_items = soup.find('div', class_='catalog-items').find_all('div', class_='position-relative')
                        for product_item in product_items:
                            try:
                                product_url = f"https://meetropol.ru{product_item.find('a').get('href')}"
                            except Exception as ex:
                                print(ex)
                                continue
                            products_urls.append(product_url)
                    except Exception as ex:
                        print(ex)
                    print(f'Обработано: {page}/{pages} страниц')

                self.get_products_data(products_urls=products_urls, session=session)

    def get_products_data(self, products_urls: list, session: Session):
        """Получаем данные товаров"""
        result_data = []
        count_urls = len(products_urls)
        print(f'Всего: {count_urls} товаров!')

        for i, product_url in enumerate(products_urls, 1):
            try:
                time.sleep(randint(1, 3))
                html = self.get_html(url=product_url, session=session)
            except Exception as ex:
                print(f"{product_url} - {ex}")
                continue

            if not html:
                continue

            soup = BeautifulSoup(html, 'lxml')
            element_list_items = soup.find_all('li', {'class': 'catalog-nav__item', 'itemprop': 'itemListElement'})

            gender_item = self.extract_gender(element_list_items)
            category_name = self.extract_category_name(element_list_items)
            subcategory_name = self.extract_subcategory_name(element_list_items)
            product_section = self.extract_product_section(soup)

            if product_section:
                name = self.extract_product_name(product_section)
                price = self.extract_product_price(product_section)
                description = self.extract_product_description(product_section)
                color = self.extract_product_color(product_section)

                result_data.append({
                    'UUID': None,
                    'Тип': category_name,
                    'Группы': subcategory_name,
                    'Пол': gender_item,
                    'Наименование': name,
                    'Внешний код': product_url,
                    'Цена товара': price,
                    'Описание': description,
                    'Характеристика:Цвет': color,
                })

                print(f'Обработано: {i}/{count_urls} товаров!')

        self.save_excel(data=result_data)

    def extract_gender(self, element_list_items):
        try:
            gender_item = element_list_items[2].text.strip()
        except Exception:
            gender_item = None
        if gender_item == 'Для неё':
            return 'Женщины'
        elif gender_item == 'Для него':
            return 'Мужчины'
        else:
            return None

    def extract_category_name(self, element_list_items):
        try:
            return element_list_items[3].text.strip()
        except Exception:
            return None

    def extract_subcategory_name(self, element_list_items):
        try:
            return element_list_items[4].text.strip()
        except Exception:
            return None

    def extract_product_section(self, soup):
        try:
            return soup.find('section', class_='product-section')
        except Exception:
            return None

    def extract_product_name(self, product_section):
        try:
            return product_section.find('h1').text.strip()
        except Exception:
            return None

    def extract_product_price(self, product_section):
        try:
            return int(''.join(i for i in product_section.find('div', class_='catalog-product__cost').find('p').text.strip() if i.isdigit()))
        except Exception:
            return None

    def extract_product_description(self, product_section):
        try:
            return product_section.find('div', class_='d-flex flex-column').find_next_sibling('p').text.strip()
        except Exception:
            return None

    def extract_product_color(self, product_section):
        try:
            return ', '.join(k for k in (c.get('title') for c in product_section.find('div', class_='filter-color__wrapper').find_all('label')) if k.isalpha())
        except Exception:
            return ' '

    def save_excel(self, data: list):
        """Сохраняем данные в Excel"""
        directory = 'results'
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = f'{directory}/result_data_products_meetropol.xlsx'
        if not os.path.exists(file_path):
            with ExcelWriter(file_path, mode='w') as writer:
                DataFrame().to_excel(writer, sheet_name='Data', index=False)

        df = read_excel(file_path, sheet_name='Data')
        num_existing_rows = len(df.index)
        dataframe = DataFrame(data)

        with ExcelWriter(file_path, mode='a', if_sheet_exists='overlay') as writer:
            dataframe.to_excel(writer, startrow=num_existing_rows + 1, header=(num_existing_rows == 0), sheet_name='Data', index=False)

        print(f'Данные сохранены в файл "{file_path}"')

    def run(self):
        """Запуск процесса сбора данных"""
        self.get_products_urls()
        execution_time = datetime.now() - self.start_time
        print('Сбор данных завершен!')
        print(f'Время работы программы: {execution_time}')


if __name__ == '__main__':
    scraper = ProductScraper(headers=headers, category_urls_list=category_urls_list)
    scraper.run()
