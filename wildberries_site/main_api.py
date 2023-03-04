import requests
import pandas as pd
import json
import csv
import os


def get_catalogs_wb():
    """получение каталога wildberries"""
    url = 'https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    data = response.json()
    with open('data/wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        print(f'Данные сохранены в wb_catalogs_data_sample.json')
    data_list = []
    for d in data:
        try:
            for child in d['childs']:
                try:
                    category_name = child['name']
                    category_url = child['url']
                    shard = child['shard']
                    query = child['query']
                    data_list.append({
                        'category_name': category_name,
                        'category_url': category_url,
                        'shard': shard,
                        'query': query})
                except:
                    continue
                try:
                    for sub_child in child['childs']:
                        category_name = sub_child['name']
                        category_url = sub_child['url']
                        shard = sub_child['shard']
                        query = sub_child['query']
                        data_list.append({
                            'category_name': category_name,
                            'category_url': category_url,
                            'shard': shard,
                            'query': query})
                except:
                    continue
        except:
            continue
    return data_list


def search_category_in_catalog(url, catalog_list):
    """пишем проверку пользовательской ссылки на наличии в каталоге"""
    try:
        for catalog in catalog_list:
            if catalog['category_url'] == url.split('https://www.wildberries.ru')[-1]:
                print(f'найдено совпадение: {catalog["category_name"]}')
                name_category = catalog['category_name']
                shard = catalog['shard']
                query = catalog['query']
                return name_category, shard, query
            else:
                pass
    except:
        print('Данный раздел не найден!')


def get_data_from_json(json_file):
    """извлекаем из json интересующие нас данные"""
    data_list = []
    for data in json_file['data']['products']:
        try:
            price = int(data["priceU"] / 100)
        except:
            price = 0
        data_list.append({
            'Наименование': data['name'],
            'id': data['id'],
            'Скидка': data['sale'],
            'Цена': price,
            'Цена со скидкой': int(data["salePriceU"] / 100),
            'Бренд': data['brand'],
            'id бренда': int(data['brandId']),
            'feedbacks': data['feedbacks'],
            'rating': data['rating'],
            'Ссылка': f'https://www.wildberries.ru/catalog/{data["id"]}/detail.aspx?targetUrl=BP'
        })
    return data_list


def get_content(shard, query, low_price=None, top_price=None):
    # вставляем ценовые рамки для уменьшения выдачи, wildberries отдает только 100 страниц
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data_list = []
    for page in range(1, 101):
        print(f'Сбор позиций со страницы {page} из 100')
        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499' \
              f'&locale=ru&page={page}&priceU={low_price * 100};{top_price * 100}' \
              f'&reg=0&regions=64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&sort=popular&spp=0&{query}'
        r = requests.get(url, headers=headers)
        data = r.json()
        data_cards = get_data_from_json(data)
        print(f'Добавлено позиций: {len(data_cards)}')
        if len(data_cards) > 0:
            data_list.extend(data_cards)
        else:
            print(f'Сбор данных завершен.')
            break
    return data_list


def save_json(data, name_category, low_price, top_price):
    """сохранение результата в json файл"""
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/{name_category}_from_{low_price}_to_{top_price}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_csv(data, name_category, low_price, top_price):
    """сохранение результата в csv файл"""
    if not os.path.exists('data'):
        os.mkdir('data')

    with open(f'data/{name_category}_from_{low_price}_to_{top_price}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ('Наименование',
             'id',
             'Скидка',
             'Цена',
             'Цена со скидкой',
             'Бренд',
             'id бренда',
             'feedbacks',
             'rating',
             'Ссылка')
        )

    with open(f'data/{name_category}_from_{low_price}_to_{top_price}.csv', 'a', encoding='utf-8') as file:
        for item in data:
            writer = csv.writer(file)
            writer.writerow(
                (item['Наименование'],
                 item['id'],
                 item['Скидка'],
                 item['Цена'],
                 item['Цена со скидкой'],
                 item['Бренд'],
                 item['id бренда'],
                 item['feedbacks'],
                 item['rating'],
                 item['Ссылка'],)
            )


def save_excel(data, filename):
    """сохранение результата в excel файл"""
    if not os.path.exists('data'):
        os.mkdir('data')

    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(f'data/{filename}.xlsx')
    df.to_excel(writer, 'data')
    writer.save()
    print(f'Все сохранено в {filename}.xlsx')


def parser(url, low_price, top_price):
    # получаем список каталогов
    catalog_list = get_catalogs_wb()
    try:
        # поиск введенной категории в общем каталоге
        name_category, shard, query = search_category_in_catalog(url=url, catalog_list=catalog_list)
        # сбор данных в найденном каталоге
        data_list = get_content(shard=shard, query=query, low_price=low_price, top_price=top_price)
        # сохранение найденных данных
        save_json(data_list, name_category, low_price, top_price)
        save_csv(data_list, name_category, low_price, top_price)
        save_excel(data_list, f'{name_category}_from_{low_price}_to_{top_price}')
    except TypeError:
        print('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')


if __name__ == '__main__':
    """ссылку на каталог или подкаталог, указывать без фильтров (без ценовых, сортировки и тд.)"""
    # url = input('Введите ссылку на категорию для сбора: ')
    # low_price = int(input('Введите минимальную сумму товара: '))
    # top_price = int(input('Введите максимульную сумму товара: '))

    """данные для теста. собераем товар с раздела велосипеды в ценовой категории от 50тыс, до 100тыс"""
    url = 'https://www.wildberries.ru/catalog/sport/vidy-sporta/velosport/velosipedy'
    low_price = 5000
    top_price = 100000

    parser(url, low_price, top_price)
