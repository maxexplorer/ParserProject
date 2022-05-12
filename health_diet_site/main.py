import requests
from bs4 import BeautifulSoup
import json
import re
import csv

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/100.0.4896.88 Mobile Safari/537.36'
}

req = requests.get(url, headers=headers)
src = req.text

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(src)

with open('index.html', 'r', encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
all_products_href = soup.find_all(class_='mzr-tc-group-item-href')

all_categories_dict = {}

for item in all_products_href:
    item_text = item.text
    item_href = 'https://health-diet.ru' + item.get('href')
    all_categories_dict[item_text] = item_href

with open('all_categories_dict.json', 'w', encoding='utf=8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open('all_categories_dict.json', 'r', encoding='utf=8') as file:
    all_categories = json.load(file)

iteration_count = len(all_categories) - 1
count = 0
print(f'Всего итераций: {iteration_count}')

for category_name, category_href in all_categories.items():

    category_name = re.sub(r"[-,' ]", "_", category_name)

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f'data/{count}_{category_name}.html', 'w', encoding='utf-8') as file:
        file.write(src)

    with open(f'data/{count}_{category_name}.html', 'r', encoding='utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    # проверяем страницы на наличие таблицы с продуктами
    alert_block = soup.find(class_='uk-alert-danger')
    if alert_block is not None:
        continue

    # собираем заголовки таблицы
    table_head = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')
    product = table_head[0].text.strip()
    calories = table_head[1].text.strip()
    proteins = table_head[2].text.strip()
    fats = table_head[3].text.strip()
    carbohydrates = table_head[4].text.strip()

    with open(f'data/{count}_{category_name}.csv', 'w', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
             product,
             proteins,
             fats,
             carbohydrates
            )
        )

    # собираем данные продуктов
    products_data = soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')

    product_info = []
    for item in products_data:
        product_tds = item.find_all('td')

        title = product_tds[0].find('a').text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        product_info.append(
            {
                'Title': title,
                'Product': product,
                'Calories': calories,
                'Proteins': proteins,
                'Fats': fats,
                'Carbohydrates': carbohydrates
            }
        )
        with open(f'data/{count}_{category_name}.csv', 'a', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                 title,
                 calories,
                 proteins,
                 fats,
                 carbohydrates
                )
            )

    with open(f'data/{count}_{category_name}.json', 'a', encoding='utf-8') as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f'# Итерация {count}. {category_name} записана...')
    iteration_count -= 1
    if iteration_count == 0:
        print('Работа завершена')
        break
    print(f'Осталось итераций: {iteration_count}')

