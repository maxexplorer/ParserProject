# calculate_profit.py

import os
import time
import glob
import requests
import pandas as pd

from configs.config import CLIENT_ID, API_KEY, API_URLS
from utils import save_excel

headers = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY
}


def get_all_products():
    """
    Получает список всех товаров со статусом IN_SALE.

    :return: Список offer_id
    """
    all_products = []
    last_id = ''
    limit = 100
    total_printed = False

    while True:
        payload = {
            'filter': {
                'visibility': 'IN_SALE'
            },
            'last_id': last_id,
            'limit': limit
        }

        response = requests.post(
            API_URLS.get('product_list'),
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print('❌ Ошибка:', response.status_code, response.text)
            break

        data = response.json()
        result = data.get('result', {})
        items = result.get('items', [])
        total = result.get('total')

        if not total_printed:
            print(f'📦 Всего продуктов: {total}')
            total_printed = True

        for item in items:
            offer_id = item.get('offer_id')
            if offer_id:
                all_products.append(offer_id)

        last_id = result.get('last_id', '')
        if not last_id:
            break

        time.sleep(1)  # 🔁 пауза между запросами

    return all_products


def load_article_info_from_excel(folder='data'):
    """
    Загружает артикулы, названия и цены из Excel-файла.

    :param folder: Папка с Excel-файлом
    :return: Словарь вида {offer_id: (название, цена)}
    """
    excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
    if not excel_files:
        print('❗ В папке data/ не найдено .xlsx файлов.')
        return {}

    df = pd.read_excel(excel_files[0])
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Артикул', df.columns[1], df.columns[2]])

    info = {}
    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        name = str(row.iloc[1]).strip()
        price = row.iloc[2]
        info[article] = (name, price)

    return info


def get_prices_and_commissions(offer_id_list, article_info):
    """
    Получает маркетинговые цены и комиссии по каждому товару.

    :param offer_id_list: Список offer_id
    :param article_info: Словарь {offer_id: (название, цена)}
    :return: Список словарей с расчётом прибыли и затрат
    """
    result_data = []
    cursor = ''
    limit = 100

    while True:
        payload = {
            'cursor': cursor,
            'filter': {
                'offer_id': offer_id_list,
                'product_id': []
            },
            'limit': limit
        }

        response = requests.post(
            API_URLS.get('product_info_prices'),
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print('❌ Ошибка:', response.status_code, response.text)
            break

        data = response.json()
        items = data.get('items', [])

        for item in items:
            offer_id = item.get('offer_id')
            price_info = item.get('price', {})
            commissions = item.get('commissions', {})

            acquiring = item.get('acquiring', 0)
            marketing_price = price_info.get('marketing_price', 0)

            fbo_delivery = commissions.get('fbo_deliv_to_customer_amount', 0)
            fbo_trans_max = commissions.get('fbo_direct_flow_trans_max_amount', 0)
            fbo_trans_min = commissions.get('fbo_direct_flow_trans_min_amount', 0)
            fbo_trans_avg = (fbo_trans_max + fbo_trans_min) / 2

            fbs_delivery = commissions.get('fbs_deliv_to_customer_amount', 0)
            fbs_trans_max = commissions.get('fbs_direct_flow_trans_max_amount', 0)
            fbs_first_mile = commissions.get('fbs_first_mile_max_amount', 0)

            name, price = article_info.get(offer_id, ('', 0))

            if name and price:
                # Расходы FBO
                expenses_fbo = round(
                    price * 1.05 +
                    acquiring * 1.05 +
                    fbo_delivery * 1.05 +
                    fbo_trans_avg * 1.10,
                    2
                )
                net_profit_fbo = round(marketing_price - expenses_fbo, 2)

                # Расходы FBS
                expenses_fbs = round(
                    price * 1.05 +
                    acquiring * 1.05 +
                    fbs_delivery * 1.05 +
                    fbs_trans_max * 1.10 +
                    fbs_first_mile * 1.05,
                    2
                )
                net_profit_fbs = round(marketing_price - expenses_fbs, 2)
            else:
                expenses_fbo = expenses_fbs = net_profit_fbo = net_profit_fbs = ''

            result_data.append({
                'Артикул': offer_id,
                'Название товара': name,
                'Расходы FBO': expenses_fbo,
                'Расходы FBS': expenses_fbs,
                'Чистая прибыль FBO': net_profit_fbo,
                'Чистая прибыль FBS': net_profit_fbs,
            })

        cursor = data.get('cursor', '')
        if not cursor:
            break

        time.sleep(1)

    return result_data


def run_product_prices() -> None:
    """
       Главная функция:
       - Получает список товаров
       - Загружает данные из Excel
       - Получает комиссии и рассчитывает прибыль
       - Сохраняет результат в Excel
       """

    print("📊 Подсчёт чистой прибыли...")

    offer_id_list = get_all_products()
    if not offer_id_list:
        print('❗ Не удалось получить список товаров.')
        return

    article_info = load_article_info_from_excel()
    if not article_info:
        print('❗ Не удалось загрузить данные из Excel.')
        return

    result = get_prices_and_commissions(offer_id_list=offer_id_list, article_info=article_info)
    if not result:
        print('❗ Нет подходящих товаров для сохранения.')
        return

    save_excel(data=result, filename_prefix='results/ozon_profit')
