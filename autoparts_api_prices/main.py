import os
import glob

import hashlib

from pandas import DataFrame, read_excel

from autotrade import get_prices_and_stocks

from config import login_autotrade, password_autotrade

salt = "1>6)/MI~{J"

url_autotrade = "https://api2.autotrade.su/?json"

# -------------------
# Формируем auth_key для autotrade
# -------------------
password_md5_autotrade = hashlib.md5(password_autotrade.encode("utf-8")).hexdigest()
auth_key_autotrade = hashlib.md5((login_autotrade + password_md5_autotrade + salt).encode("utf-8")).hexdigest()

# -------------------
# Заголовки
# -------------------
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

def load_article_info_from_excel(df: DataFrame):
    """
    Загружает артикулы, названия и цены из Excel-файла.

    :param folder: Папка с Excel-файлом
    :return: Словарь вида {offer_id: (название, цена)}
    """

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Артикул', df.columns[1], df.columns[2]])

    article_info = []
    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        name = str(row.iloc[2]).strip()
        price = row.iloc[3]
        article_info.append(article)


    return article_info

def main():
    autotrade_df = read_excel('data/SAT autotrade.xlsx', header=0, sheet_name=0)
    abcp_df = read_excel('data/ОЕМ abcp.xlsx', header=0, sheet_name=0)

    autotrade_article = load_article_info_from_excel(df=autotrade_df)
    abcp_df = load_article_info_from_excel(df=abcp_df)

    get_prices_and_stocks(url_autotrade, headers, auth_key_autotrade, autotrade_article)




if __name__ == '__main__':
    main()