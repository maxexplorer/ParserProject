import datetime
import json
import asyncio
import aiohttp

start_time = datetime.datetime.now()
data_list = []


async def get_pages_data(session, page):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Is-Ajax-Request': 'X-Is-Ajax-Request',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/101.0.4951.67 Safari/537.36'
    }
    url = "https://roscarservis.ru/catalog/legkovye/?sort%5Bprice%5D=asc&form_id=catalog_filter_form&filter_mode" \
          f"=params&filter_type=tires&diskType=1&arCatalogFilter_458_1500340406=Y&set_filter=Y&PAGEN_1={page}"

    try:
        async with session.get(url=url, headers=headers) as response:
            response_json = await response.text()
            data_json = json.loads(response_json)

            items = data_json['items']

            possible_stores = ['discountStores', 'fortochkiSrores', 'commonStores']
            for item in items:
                total_amount = 0
                item_name = item['name']
                item_price = item['price']
                item_img = f"https://roscarservis.ru'{item['imgSrc']}"
                item_url = f"https://roscarservis.ru{item['url']}"

                stores = []
                for ps in possible_stores:
                    if ps in item:
                        if item[ps] is None or len(item[ps]) < 1:
                            continue
                        else:
                            for store in item[ps]:
                                store_name = store['STORE_NAME']
                                store_price = store['PRICE']
                                store_amount = store['AMOUNT']
                                total_amount += int(store['AMOUNT'])

                                stores.append(
                                    {
                                        'store_name': store_name,
                                        'store_price': store_price,
                                        'store_amount': store_amount
                                    }
                                )
                data_list.append(
                    [
                        {
                            'name': item_name,
                            'price': item_price,
                            'img': item_img,
                            'url': item_url,
                            'stores': stores,
                            'total_amount': total_amount
                        }
                    ]
                )

            print(f'[INFO] Обработал {page}')
    except Exception as ex:
        print(f'{page}: {ex}')


async def gather_data():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Is-Ajax-Request': 'X-Is-Ajax-Request',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/101.0.4951.67 Safari/537.36'
    }
    url = "https://roscarservis.ru/catalog/legkovye/?sort%5Bprice%5D=asc&form_id=catalog_filter_form&filter_mode" \
          "=params&filter_type=tires&diskType=1&arCatalogFilter_458_1500340406=Y&set_filter=Y&PAGEN_1=1"

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        response_json = await response.json(content_type='text/html')
        # response_json = await response.json(content_type=None)

        # response_json = await response.text()
        # data_json = json.loads(response_json)
        # pages_count = data_json['pageCount']

        pages_count = response_json['pageCount']
        print(pages_count)



        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_pages_data(session, page))
            await asyncio.sleep(0.05)

            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.get_event_loop().run_until_complete(gather_data())
    cur_time = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')

    with open(f'data/data_{cur_time}_async.json', 'a', encoding='utf-8') as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)

    diff_time = datetime.datetime.now() - start_time
    print(diff_time)


if __name__ == '__main__':
    main()
