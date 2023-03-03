import json
import os

import requests
from fake_useragent import UserAgent

useragent = UserAgent()

url = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=%2Fproduct%2Fsmartfon-huawei-nova-y70-4-128-gb-goluboy-622866113"

headers = {
    'User-Agent': useragent.random
}

response = requests.get(url=url, headers=headers)
print(response)
data = response.json()

if not os.path.exists('data'):
    os.mkdir('data')

with open('data/data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
