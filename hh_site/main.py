import json
import os

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


def get_data():
    useragent = UserAgent()

    text = 'Административный директор'

    page = 10

    url = f"https://hh.ru/search/resume?text={text}&area=1&isDefaultArea=true&exp_period=all_time&logic=normal&" \
          f"pos=full_text&fromSearchLine=false&page={page}"

    headers = {
        'Accept': '*/*',
        'User-Agent': useragent.random
    }

    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

    soup = BeautifulSoup(response.text, 'lxml')

    elem = soup.find(attrs={'key': 'value'})


    print(response.status_code)

    if not os.path.exists('data'):
        os.mkdir('data')

    with open('data/hh_data.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()