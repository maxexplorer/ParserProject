# main.py

import hashlib

from autotrade import get_prices_and_stocks

from config import login_autotrade, password_autotrade, login_abcp, password_abcp
from utils import load_article_info_from_excel, save_excel

salt = "1>6)/MI~{J"

url_autotrade = "https://api2.autotrade.su/?json"
url_adcp = "https://id34451.public.api.abcp.ru"

# -------------------
# Формируем auth_key для autotrade
# -------------------
password_md5_autotrade = hashlib.md5(password_autotrade.encode("utf-8")).hexdigest()
auth_key_autotrade = hashlib.md5((login_autotrade + password_md5_autotrade + salt).encode("utf-8")).hexdigest()

# -------------------
# Формируем auth_key для adcp
# -------------------
password_md5_adcp = hashlib.md5(password_abcp.encode("utf-8")).hexdigest()

# -------------------
# Заголовки
# -------------------
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


def main():
    autotrade_file_path = 'data/SAT autotrade.xlsx'
    abcp_file_path = 'data/ОЕМ abcp.xlsx'

    autotrade_articles = load_article_info_from_excel(autotrade_file_path)

    autotrade_data = get_prices_and_stocks(
        url_autotrade,
        headers,
        auth_key_autotrade,
        autotrade_articles
    )

    save_excel(autotrade_data)


if __name__ == '__main__':
    main()
