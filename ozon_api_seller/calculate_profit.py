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

    article_info = {}
    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        name = str(row.iloc[1]).strip()
        cost_price = row.iloc[2]
        article_info[article] = (name, cost_price)

    return article_info


def get_prices_and_commissions(article_info):
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
                'offer_id': [],
                'product_id': [],
                'visibility': 'IN_SALE'
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
            marketing_seller_price = price_info.get('marketing_seller_price', 0)

            fbo_delivery = commissions.get('fbo_deliv_to_customer_amount', 0)
            fbo_trans_max = commissions.get('fbo_direct_flow_trans_max_amount', 0)
            fbo_trans_min = commissions.get('fbo_direct_flow_trans_min_amount', 0)
            fbo_trans_avg = (fbo_trans_max + fbo_trans_min) / 2

            fbs_delivery = commissions.get('fbs_deliv_to_customer_amount', 0)
            fbs_trans_max = commissions.get('fbs_direct_flow_trans_max_amount', 0)
            fbs_first_mile = commissions.get('fbs_first_mile_max_amount', 0)

            name, cost_price = article_info.get(offer_id, ('', 0))

            if name and cost_price:
                # Расходы FBO
                expenses_fbo = round(
                    marketing_seller_price * 0.27 +
                    marketing_seller_price * 0.07 +
                    cost_price * 1.05 +
                    cost_price * 0.5 +
                    acquiring * 1.05 +
                    fbo_delivery * 1.05 +
                    fbo_trans_avg * 1.10,
                    2
                )
                net_profit_fbo = round(marketing_seller_price - expenses_fbo, 2)

                # Расходы FBS
                expenses_fbs = round(
                    marketing_seller_price * 0.305 +
                    marketing_seller_price * 0.07 +
                    cost_price * 1.05 +
                    cost_price * 0.5 +
                    acquiring * 1.05 +
                    fbs_delivery * 1.05 +
                    fbs_trans_max * 1.10 +
                    fbs_first_mile * 1.05,
                    2
                )
                net_profit_fbs = round(marketing_seller_price - expenses_fbs, 2)
            else:
                expenses_fbo = expenses_fbs = net_profit_fbo = net_profit_fbs = ''

            result_data.append({
                'Артикул': offer_id,
                'Название товара': name,
                'Расходы FBO': expenses_fbo,
                'Расходы FBS': expenses_fbs,
                'Остаток на расходы FBO': net_profit_fbo,
                'Остаток на расходы FBS': net_profit_fbs,
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

    article_info = load_article_info_from_excel()
    if not article_info:
        print('❗ Не удалось загрузить данные из Excel.')
        return

    result = get_prices_and_commissions(article_info=article_info)
    if not result:
        print('❗ Нет подходящих товаров для сохранения.')
        return

    save_excel(data=result, filename_prefix='results/ozon_profit')
