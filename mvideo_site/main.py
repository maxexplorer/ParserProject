import requests
import json


def get_data():
    cookies = {
        '__js_p_': '242,900,0,1,0',
        '__jhash_': '456',
        '__jua_': 'Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F103.0.0.0%20Safari%2F537.36',
        '__hash_': '5391e56a48743a3de5abe53c0af359a3',
        '__lhash_': 'b0a8a58dbc00e93b0e937c6d69721f29',
        'CACHE_INDICATOR': 'false',
        'COMPARISON_INDICATOR': 'false',
        'HINTS_FIO_COOKIE_NAME': '1',
        'MVID_2_exp_in_1': '1',
        'MVID_AB_SERVICES_DESCRIPTION': 'var4',
        'MVID_ADDRESS_COMMENT_AB_TEST': '2',
        'MVID_BLACK_FRIDAY_ENABLED': 'true',
        'MVID_CALC_BONUS_RUBLES_PROFIT': 'true',
        'MVID_CART_MULTI_DELETE': 'true',
        'MVID_CATALOG_STATE': '1',
        'MVID_CITY_ID': 'CityCZ_975',
        'MVID_FILTER_CODES': 'true',
        'MVID_FILTER_TOOLTIP': '1',
        'MVID_FLOCKTORY_ON': 'true',
        'MVID_GEOLOCATION_NEEDED': 'true',
        'MVID_GET_LOCATION_BY_DADATA': 'DaData',
        'MVID_GIFT_KIT': 'true',
        'MVID_GTM_DELAY': 'true',
        'MVID_GUEST_ID': '20997355285',
        'MVID_IS_NEW_BR_WIDGET': 'true',
        'MVID_KLADR_ID': '7700000000000',
        'MVID_LAYOUT_TYPE': '1',
        'MVID_LP_SOLD_VARIANTS': '3',
        'MVID_MCLICK': 'true',
        'MVID_MOBILE_FILTERS': 'false',
        'MVID_NEW_ACCESSORY': 'true',
        'MVID_NEW_DESKTOP_FILTERS': 'true',
        'MVID_NEW_LK_CHECK_CAPTCHA': 'true',
        'MVID_NEW_LK_OTP_TIMER': 'true',
        'MVID_NEW_MBONUS_BLOCK': 'true',
        'MVID_NEW_SUGGESTIONS': 'true',
        'MVID_PROMO_CATALOG_ON': 'true',
        'MVID_REGION_ID': '1',
        'MVID_REGION_SHOP': 'S002',
        'MVID_SERVICES': '111',
        'MVID_SERVICES_MINI_BLOCK': 'var2',
        'MVID_TAXI_DELIVERY_INTERVALS_VIEW': 'new',
        'MVID_TIMEZONE_OFFSET': '3',
        'MVID_WEBP_ENABLED': 'true',
        'NEED_REQUIRE_APPLY_DISCOUNT': 'true',
        'PICKUP_SEAMLESS_AB_TEST': '2',
        'PRESELECT_COURIER_DELIVERY_FOR_KBT': 'false',
        'PROMOLISTING_WITHOUT_STOCK_AB_TEST': '2',
        'flacktory': 'no',
        'searchType2': '2',
        'MVID_ENVCLOUD': 'primary',
        'mindboxDeviceUUID': '13f51313-f0b6-4d3e-b911-776c9d49fabf',
        'directCrm-session': '%7B%22deviceGuid%22%3A%2213f51313-f0b6-4d3e-b911-776c9d49fabf%22%7D',
        'popmechanic_sbjs_migrations': 'popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1',
        '_ga': 'GA1.2.634447956.1656951246',
        '_gid': 'GA1.2.1285090603.1656951247',
        '_ym_d': '1656951247',
        '_ym_uid': '1656951247724262333',
        'partnerSrc': 'yandex',
        '__SourceTracker': 'yandex__organic',
        'admitad_deduplication_cookie': 'yandex__organic',
        '__sourceid': 'yandex',
        '__cpatrack': 'yandex_organic',
        '__allsource': 'yandex',
        'SMSError': '',
        'authError': '',
        'tmr_lvidTS': '1656951248389',
        'tmr_lvid': '2fe1a6f5924a8442bc22cb516efa0745',
        'gdeslon.ru.__arc_domain': 'gdeslon.ru',
        'gdeslon.ru.user_id': 'e94e1f97-b860-4988-915f-76a2b8630d2a',
        '_ym_isad': '2',
        'st_uid': 'c510fc88aac68fc0de159a2996a9d88e',
        'advcake_track_id': '4c4ef95c-1c03-a28f-b1dd-650cc2859b08',
        'advcake_session_id': 'a76eec11-b152-c583-0d21-ea3eac5addb8',
        'advcake_track_url': 'https%3A%2F%2Fwww.mvideo.ru%2F%3Futm_source%3Dyandex%26utm_medium%3Dorganic%26utm_campaign%3Dyandex%26utm_referrer%3Dyandex',
        'advcake_utm_partner': 'yandex',
        'advcake_utm_webmaster': '',
        'advcake_click_id': '',
        'afUserId': '02e13e18-9bab-42bd-87d0-4fc38fa40337-p',
        'uxs_uid': '578dd240-fbb4-11ec-bd78-2b81284a352f',
        'AF_SYNC': '1656951252421',
        'flocktory-uuid': '9c7e4198-584f-43b0-8038-774b637f6c2d-0',
        'BIGipServeratg-ps-prod_tcp80': '2953108490.20480.0000',
        'bIPs': '-1323973254',
        'tmr_detect': '0%7C1656951257945',
        'JSESSIONID': 'Q23GvDSdh0klJ92pQnb5PpXh1JycMsPyDNffZ2cJydb3wwYv6LyZ!-239921941',
        'tmr_reqNum': '19',
        '_ga_CFMZTSS5FM': 'GS1.1.1656951246.1.1.1656951493.0',
        '_ga_BNX5WPP3YK': 'GS1.1.1656951246.1.1.1656951493.60',
        'ADRUM_BT': 'R:98|g:b700752c-1435-42a2-840e-b9779f6ffddd15628122',
    }

    headers = {
        'authority': 'www.mvideo.ru',
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # Requests sorts cookies= alphabetically
        # 'cookie': '__js_p_=242,900,0,1,0; __jhash_=456; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F103.0.0.0%20Safari%2F537.36; __hash_=5391e56a48743a3de5abe53c0af359a3; __lhash_=b0a8a58dbc00e93b0e937c6d69721f29; CACHE_INDICATOR=false; COMPARISON_INDICATOR=false; HINTS_FIO_COOKIE_NAME=1; MVID_2_exp_in_1=1; MVID_AB_SERVICES_DESCRIPTION=var4; MVID_ADDRESS_COMMENT_AB_TEST=2; MVID_BLACK_FRIDAY_ENABLED=true; MVID_CALC_BONUS_RUBLES_PROFIT=true; MVID_CART_MULTI_DELETE=true; MVID_CATALOG_STATE=1; MVID_CITY_ID=CityCZ_975; MVID_FILTER_CODES=true; MVID_FILTER_TOOLTIP=1; MVID_FLOCKTORY_ON=true; MVID_GEOLOCATION_NEEDED=true; MVID_GET_LOCATION_BY_DADATA=DaData; MVID_GIFT_KIT=true; MVID_GTM_DELAY=true; MVID_GUEST_ID=20997355285; MVID_IS_NEW_BR_WIDGET=true; MVID_KLADR_ID=7700000000000; MVID_LAYOUT_TYPE=1; MVID_LP_SOLD_VARIANTS=3; MVID_MCLICK=true; MVID_MOBILE_FILTERS=false; MVID_NEW_ACCESSORY=true; MVID_NEW_DESKTOP_FILTERS=true; MVID_NEW_LK_CHECK_CAPTCHA=true; MVID_NEW_LK_OTP_TIMER=true; MVID_NEW_MBONUS_BLOCK=true; MVID_NEW_SUGGESTIONS=true; MVID_PROMO_CATALOG_ON=true; MVID_REGION_ID=1; MVID_REGION_SHOP=S002; MVID_SERVICES=111; MVID_SERVICES_MINI_BLOCK=var2; MVID_TAXI_DELIVERY_INTERVALS_VIEW=new; MVID_TIMEZONE_OFFSET=3; MVID_WEBP_ENABLED=true; NEED_REQUIRE_APPLY_DISCOUNT=true; PICKUP_SEAMLESS_AB_TEST=2; PRESELECT_COURIER_DELIVERY_FOR_KBT=false; PROMOLISTING_WITHOUT_STOCK_AB_TEST=2; flacktory=no; searchType2=2; MVID_ENVCLOUD=primary; mindboxDeviceUUID=13f51313-f0b6-4d3e-b911-776c9d49fabf; directCrm-session=%7B%22deviceGuid%22%3A%2213f51313-f0b6-4d3e-b911-776c9d49fabf%22%7D; popmechanic_sbjs_migrations=popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; _ga=GA1.2.634447956.1656951246; _gid=GA1.2.1285090603.1656951247; _ym_d=1656951247; _ym_uid=1656951247724262333; partnerSrc=yandex; __SourceTracker=yandex__organic; admitad_deduplication_cookie=yandex__organic; __sourceid=yandex; __cpatrack=yandex_organic; __allsource=yandex; SMSError=; authError=; tmr_lvidTS=1656951248389; tmr_lvid=2fe1a6f5924a8442bc22cb516efa0745; gdeslon.ru.__arc_domain=gdeslon.ru; gdeslon.ru.user_id=e94e1f97-b860-4988-915f-76a2b8630d2a; _ym_isad=2; st_uid=c510fc88aac68fc0de159a2996a9d88e; advcake_track_id=4c4ef95c-1c03-a28f-b1dd-650cc2859b08; advcake_session_id=a76eec11-b152-c583-0d21-ea3eac5addb8; advcake_track_url=https%3A%2F%2Fwww.mvideo.ru%2F%3Futm_source%3Dyandex%26utm_medium%3Dorganic%26utm_campaign%3Dyandex%26utm_referrer%3Dyandex; advcake_utm_partner=yandex; advcake_utm_webmaster=; advcake_click_id=; afUserId=02e13e18-9bab-42bd-87d0-4fc38fa40337-p; uxs_uid=578dd240-fbb4-11ec-bd78-2b81284a352f; AF_SYNC=1656951252421; flocktory-uuid=9c7e4198-584f-43b0-8038-774b637f6c2d-0; BIGipServeratg-ps-prod_tcp80=2953108490.20480.0000; bIPs=-1323973254; tmr_detect=0%7C1656951257945; JSESSIONID=Q23GvDSdh0klJ92pQnb5PpXh1JycMsPyDNffZ2cJydb3wwYv6LyZ!-239921941; tmr_reqNum=19; _ga_CFMZTSS5FM=GS1.1.1656951246.1.1.1656951493.0; _ga_BNX5WPP3YK=GS1.1.1656951246.1.1.1656951493.60; ADRUM_BT=R:98|g:b700752c-1435-42a2-840e-b9779f6ffddd15628122',
        'referer': 'https://www.mvideo.ru/noutbuki-planshety-komputery-8/planshety-195/f/skidka=da/tolko-v-nalichii=da',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'x-set-application-id': '8b8808f6-dc17-4579-b3c8-db765dd1e548',
    }

    params = {
        'categoryId': '195',
        'offset': '0',
        'limit': '24',
        'filterParams': [
            'WyJza2lka2EiLCIiLCJkYSJd',
            'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
        ],
        'doTranslit': 'true',
    }

    response = requests.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                            headers=headers).json()

    products_ids = response.get('body').get('products')

    with open('data/1_products_ids.json', 'w', encoding='utf-8') as file:
        json.dump(products_ids, file, indent=4, ensure_ascii=False)

    json_data = {
        'productIds': products_ids,
        'mediaTypes': [
            'images',
        ],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': [
            'KEY',
        ],
        'propertiesConfig': {
            'propertiesPortionSize': 5,
        },
        'multioffer': False,
    }

    response = requests.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                             json=json_data).json()

    with open('data/2_items.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)

    products_ids_str = ','.join(products_ids)

    params = {
        'productIds': products_ids_str,
        'addBonusRubles': 'true',
        'isPromoApplied': 'true',
    }

    response = requests.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                            headers=headers).json()

    with open('data/3_prices.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)

    items_prices = {}

    materials_prices = response.get('body').get('materialPrices')

    for item in materials_prices:
        item_id = item.get('price').get('productId')
        item_base_price = item.get('price').get('basePrice')
        item_sale_price = item.get('price').get('salePrice')
        item_bonus = item.get('bonusRubles').get('total')

        items_prices[item_id] = {
            'item_basePrice': item_base_price,
            'item_salePrice': item_sale_price,
            'item_bonus': item_bonus
        }

    with open('data/4_items_prices.json', 'w', encoding='utf-8') as file:
        json.dump(items_prices, file, indent=4, ensure_ascii=False)


def get_result():
    with open('data/2_items.json', encoding='utf-8') as file:
        products_data = json.load(file)

    with open('data/4_items_prices.json', encoding='utf-8') as file:
        products_prices = json.load(file)

    products_data = products_data.get('body').get('products')

    for item in products_data:
        product_id = item.get('productId')

        if product_id in products_prices:
            prices = products_prices[product_id]

            item['item_basePrice'] = prices['item_basePrice']
            item['item_salePrice'] = prices['item_salePrice']
            item['item_bonus'] = prices['item_bonus']

    with open('data/5_result.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)


def main():
    get_data()
    get_result()


if __name__ == '__main__':
    main()
