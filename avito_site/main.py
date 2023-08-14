import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json


def get_html(url):
    options = Options()
    options.add_argument('User-Agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
        options=options
    )
    browser.maximize_window()

    try:
        browser.get(url=url)

        # time.sleep(5)
        browser.implicitly_wait(5)

        html = browser.page_source
        return html
    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


def get_content(html):
    cards = []
    soup = BeautifulSoup(html, 'lxml')

    items = soup.find_all('div', {'data-marker': 'item'})

    for item in items:
        try:
            title = item.find('h3', itemprop='name').text.strip()
        except Exception:
            title = None
        try:
            price = int(item.find('span', itemprop='offers').text.strip().replace('\xa0', '').replace('₽', ''))
        except Exception:
            price = None
        try:
            params = item.find('div', {'data-marker': 'item-specific-params'}).text.strip().replace('\xa0', '')
        except Exception:
            params = None
        try:
            description = item.find('div', class_='iva-item-descriptionStep-C0ty1').text.strip().replace('\n', '')
        except Exception:
            description = None
        try:
            address = item.find('div', class_='geo-address-fhHd0 text-text-LurtD text-size-s-BxGpL').text.strip()
        except Exception:
            address = None
        try:
            url = 'https://www.avito.ru/' + item.find('a').get('href')
        except Exception:
            url = None

        cards.append(
            {
                'title': title,
                'price': price,
                'params': params,
                'description': description,
                'address': address,
                'url': url
            }
        )
    return cards


def save_json(data):
    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    pages = int(input('Введите количество страниц: '))
    brand = 'samsung'
    for page in range(1, pages + 1):
        url = f"https://www.avito.ru/all/telefony/mobilnye_telefony/samsung-ASgBAgICAkS0wA2crzmwwQ2I_Dc?cd=1&p={page}&q={brand}"
        html = get_html(url=url)
        cards = get_content(html)
        save_json(cards)
        if not os.path.exists('data'):
            os.mkdir('data')
        with open('data/index.html', 'w', encoding='utf-8') as file:
            file.write(html)
    with open('data/index.html', 'r', encoding='utf-8') as file:
        html = file.read()
    cards = get_content(html)
    print(len(cards))
    print(get_content(html))


if __name__ == '__main__':
    main()
