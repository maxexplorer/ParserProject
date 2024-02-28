import requests

urls_list = [
    "https://www.wildberries.ru/brands/97714537-belgatto",
    "https://www.wildberries.ru/brands/rifforma"
]


def get_id_brand(url):

    headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Referer': url,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    brand = url.split('brands')[-1].strip()

    with requests.Session() as session:
        response = session.get(f'https://static-basket-01.wbbasket.ru/vol0/data/brands{brand}.json', headers=headers)

    json_data = response.json()

    id_brand = json_data.get('id')

    return id_brand


def get_data():

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wildberries.ru',
        'Referer': 'https://www.wildberries.ru/brands/97714537-belgatto',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'appType': '1',
        'brand': '97714537',
        'curr': 'rub',
        'dest': '-1257786',
        'sort': 'popular',
        'spp': '30',
    }

    response = requests.get('https://catalog.wb.ru/brands/b/catalog', params=params, headers=headers)

    print(response.json())


def main():
    for url in urls_list:
        get_id_brand(url=url)
    # get_data()


if __name__ == '__main__':
    main()
