import os
import json

from requests import Session

from configs.config import headers
from configs.config import params


# Функция получения id категорий
def get_id_categories(headers: dict, params: dict) -> None:
    id_categories_data = []

    with Session() as session:
        try:
            response = session.get(
                'https://www.zara.com/es/en/categories',
                headers=headers,
                params=params,
                timeout=60
            )

            if response.status_code != 200:
                print(f'status_code: {response.status_code}')

            json_data = response.json()
        except Exception as ex:
            print(f'get_id_categories: {ex}')

    try:
        category_items = json_data['categories']
    except Exception:
        category_items = []

    for category_item in category_items[:3]:
        category_name = category_item.get('sectionName')
        subcategory_items = category_item.get('subcategories')
        for subcategory_item in subcategory_items:
            subcategory_name = subcategory_item.get('name')
            subcategory_id = subcategory_item.get('id')
            redirect_category_id = subcategory_item.get('redirectCategoryId')
            category_id = redirect_category_id if redirect_category_id else subcategory_id
            id_categories_data.append((subcategory_name, category_id))
            # print(f"('{subcategory_name}', {category_id}),")
            if category_name == 'KID':
                subcategory_kid_items = subcategory_item.get('subcategories')
                for subcategory_kid_item in subcategory_kid_items:
                    subcategory_kid_name = subcategory_kid_item.get('name')
                    subcategory_kid_id = subcategory_kid_item.get('id')
                    redirect_category_kid_id = subcategory_kid_item.get('redirectCategoryId')
                    category_kid_id = redirect_category_kid_id if redirect_category_kid_id else subcategory_kid_id
                    id_categories_data.append((subcategory_kid_name, category_kid_id))


    with open('data/id_categories_list_1.txt', 'w', encoding='utf-8') as file:
        print(*id_categories_data, file=file, sep=',\n')

def get_products_data(headers: dict):

    #
    # headers = {
    #     'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    #     'X-KL-kfa-Ajax-Request': 'Ajax_Request',
    #     'Referer': 'https://www.zara.com/es/en/woman-blazers-l1055.html?v1=2352684',
    #     'sec-ch-ua-mobile': '?0',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    #     'sec-ch-ua-platform': '"Windows"',
    # }
    #
    # params = {
    #     'productIds': ['348188026', '348201363'],
    #     'ajax': 'true',
    # }
    #
    # response = requests.get('https://www.zara.com/es/en/products-details', params=params, headers=headers)
    #
    # with open('data/products-details.json', 'w', encoding='utf-8') as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    with open('data/products-details.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    name = json_data[1]['name']

    print(name)

    # try:
    #     products_data = json_data['productGroups'][0]['elements']
    # except Exception:
    #     products_data = []
    #
    # for item in products_data:
    #     id_product = item['commercialComponents'][0]['id']
    #     reference = item['commercialComponents'][0]['reference']
    #     print(reference)


def main():
    get_id_categories(headers=headers, params=params)

if __name__ == '__main__':
    main()