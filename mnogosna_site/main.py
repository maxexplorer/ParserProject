import requests
import json
import os
from config import cookies, headers

# cookies = {'your': 'cookies'}
# headers = {'your': 'headers'}


def get_data():
    data = {
        'act': 'getListSizes',
        'size_id': '13501',
        'list': '[1373,1438691,329,1096476,9622,1096685,11290,330,5189,11294,1309,9624,387,327,1438686,5187,11293,1438764,9620,1096670,855,11295,5186,13191,1096689,11298,349,5184,6603]',
    }

    with requests.Session as session:
        response = session.post('https://mnogosna.ru/local/ajax/product.php', cookies=cookies, headers=headers, data=data)

    with open('data/data.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()
