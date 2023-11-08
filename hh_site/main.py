import json
import os

import requests


# url = "https://api.hh.ru/areas/"
url = "https://api.hh.ru/vacancies/"


response = requests.get(url=url)

if not os.path.exists('data'):
    os.mkdir('data')

with open('data/hh_data.json', 'w', encoding='utf-8') as file:
    json.dump(response.json(), file, indent=4, ensure_ascii=False)

