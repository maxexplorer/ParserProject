import json

import requests
import os
import csv
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931'
}

start_time = datetime.now()

url = "https://asko-russia.ru/"


# Получаем html разметку страницы
def get_html(url: str, headers: dict, session: requests.sessions.Session) -> str:
    """
    :param url: str
    :param headers: dict
    :param session: requests.sessions.Session
    :return: str
    """

    try:
        response = session.get(url=url, headers=headers, timeout=60)
        print(response.status_code)
        html = response.text
        return html
    except Exception as ex:
        print(ex)

def get_json():
    import requests

    cookies = {
        'K_REGION': 'MSK',
        'BITRIX_SM_SALE_UID': '139581249',
        'tmr_lvid': '00cdee5f915b5bfed9acc2cd6d6b51e6',
        'tmr_lvidTS': '1701540233555',
        'BX_USER_ID': 'f7a5a556ad009258e524a1cc0ce603b3',
        '_ym_uid': '1701540237864915058',
        '_ym_d': '1701540237',
        'YM_CLIENT_ID': '1701540237864915058',
        '_gid': 'GA1.2.114904730.1701938240',
        '_ym_isad': '2',
        'SESSIONID': 'gidlv2mbqv7g4jqhqdise7cqgo',
        '_ym_visorc': 'w',
        'K_SORT': 'HIT',
        'K_ORDER': 'DESC',
        'tmr_detect': '0%7C1701944039108',
        '_ga_QLWYNG1N96': 'GS1.1.1701943938.5.1.1701944090.60.0.0',
        '_ga': 'GA1.2.431812079.1701540233',
        '_gat_gtag_UA_35411430_1': '1',
    }

    headers = {
        'authority': 'asko-russia.ru',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': 'K_REGION=MSK; BITRIX_SM_SALE_UID=139581249; tmr_lvid=00cdee5f915b5bfed9acc2cd6d6b51e6; tmr_lvidTS=1701540233555; BX_USER_ID=f7a5a556ad009258e524a1cc0ce603b3; _ym_uid=1701540237864915058; _ym_d=1701540237; YM_CLIENT_ID=1701540237864915058; _gid=GA1.2.114904730.1701938240; _ym_isad=2; SESSIONID=gidlv2mbqv7g4jqhqdise7cqgo; _ym_visorc=w; K_SORT=HIT; K_ORDER=DESC; tmr_detect=0%7C1701944039108; _ga_QLWYNG1N96=GS1.1.1701943938.5.1.1701944090.60.0.0; _ga=GA1.2.431812079.1701540233; _gat_gtag_UA_35411430_1=1',
        'origin': 'https://asko-russia.ru',
        'referer': 'https://asko-russia.ru/catalog/stiralnye_mashiny/professionalnaya-stiralnaya-mashina-asko-wmc8947vi-s.html',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'action': 'GetDataProduct',
        'ID': '52700',
        'items': '52644',
    }

    response = requests.post('https://asko-russia.ru/_ecommerce/ecommerce.php', cookies=cookies, headers=headers,
                             data=data)
    with open('json_data.json', 'w', encoding='utf-8') as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)

def main():
    # session = requests.Session()
    #
    # get_html(url=url, headers=headers, session=session)
    get_json()


if __name__ == '__main__':
    main()
