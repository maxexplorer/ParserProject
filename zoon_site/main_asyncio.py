import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import unquote
import json

url = "https://rostov.zoon.ru/hotels/"

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

start_time = time.time()

result_list = []


def get_search_html(url):
    browser = webdriver.Chrome(
        executable_path="C:/Users/Макс/PycharmProjects/ParserProject/chromedriver/chromedriver.exe",
    )
    browser.maximize_window()

    try:
        browser.get(url=url)
        time.sleep(5)

        while True:
            element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'catalog-button-showMore'))
            )

            if not browser.find_elements(By.CLASS_NAME, 'js-next-page'):
                if not os.path.exists('data'):
                    os.mkdir('data')
                with open('data/page_source.html', 'w', encoding='utf-8') as file:
                    file.write(browser.page_source)
                break
            else:
                actions = ActionChains(browser)
                actions.move_to_element(element).click().perform()
                time.sleep(5)

    except Exception as ex:
        print(ex)
    finally:
        browser.close()
        browser.quit()


def get_items_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('div', class_='minicard-item__info')

    urls = []
    for item in items_divs:
        item_url = item.find('h2', class_='minicard-item__title').find('a').get('href')
        urls.append(item_url)

    with open('data/items_urls.txt', 'w', encoding='utf-8') as file:
        print(*urls, file=file, sep='\n')

    return '[INFO] Urls collected successfully!'


async def get_data(session, i, url, urls_count):
    async with session.get(url=url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')

        try:
            item_name = soup.find('span', {'itemprop': 'name'}).text.strip()
        except Exception:
            item_name = None

        item_phones_list = []
        try:
            item_phones = soup.find('div', class_='service-phones-list').find_all('a', class_='js-phone-number')
            for phone in item_phones:
                item_phone = phone.get('href').split(':')[-1].strip()
                item_phones_list.append(item_phone)
        except Exception:
            item_phones_list = None

        try:
            item_address = soup.find('address', class_='iblock').text.strip().replace(' ', ' ')
        except Exception:
            item_address = None
        try:
            item_site = soup.find('div', class_='service-website-value').text.strip()
        except Exception:
            item_site = None

        social_networks_list = []
        try:
            item_social_networks = soup.find('div', class_='js-service-socials').find_all('a')
            for sn in item_social_networks:
                sn_url = sn.get('href')
                sn_url = unquote(sn_url.split('?to=')[1].split('&')[0])
                social_networks_list.append(sn_url)
        except Exception:
            social_networks_list = None

        result_list.append(
            {
                'item_name': item_name,
                'item_url': url,
                'item_phones_list': item_phones_list,
                'item_address': item_address,
                'item_site': item_site,
                'social_networks_list': social_networks_list
            }
        )

        print(f'[+] Processed {i}/{urls_count}')



    return '[INFO] Data collected successfully!'


async def gather_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls_list = [url.strip() for url in file.readlines()]

    urls_count = len(urls_list)

    tasks = []

    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls_list[:10], 1):
            task = asyncio.create_task(get_data(session, i, url, urls_count))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():
    get_search_html(url=url)
    print(get_items_urls(file_path='data/page_source.html'))
    asyncio.get_event_loop().run_until_complete(gather_data(file_path='data/items_urls.txt'))

    with open('data/result_list_asyncio.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    finish_time = time.time() - start_time
    print(f'Время работы программы: {finish_time}')


if __name__ == '__main__':
    main()
