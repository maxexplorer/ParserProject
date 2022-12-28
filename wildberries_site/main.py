import requests
from bs4 import BeautifulSoup
import os
import time
import json

# url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru.json"
url = "https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=3,6,19,21,8&curr=rub&dest=-1059500,-72639,-1754564,-4653095&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query=%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0&reg=0&regions=80,64,83,4,38,33,86,30,40,48,1,66,31,68,22&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"
# url = "https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=3,6,19,21,8&curr=rub&dest=-1059500,-72639,-1754564,-4653095&emp=0&lang=ru&locale=ru&page=2&pricemarginCoeff=1.0&query=%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0&reg=0&regions=80,64,83,4,38,33,86,30,40,48,1,66,31,68,22&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/108.0.0.0 Safari/537.36'
}


def get_data(url, headers):
    response = requests.get(url=url, headers=headers)

    data = response.json()

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/data_json.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    get_data(url=url, headers=headers)


if __name__ == '__main__':
    main()
