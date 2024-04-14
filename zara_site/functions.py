import requests

from googletrans import Translator


# Функция для перевода европейских размеров в российские
def sizes_format(gender: str, size_eur: str) -> str:
    sizes_dict = {
        'ЖЕНЩИНЫ': {
            'XXS': '40',
            'XS': '42',
            'S': '44',
            'M': '46;48',
            'L': '48;50',
            'M-L': '46;50',
            'XL': '50;52',
            'XXL': '54',
        },
        'МУЖЧИНЫ': {
            'XS': '44',
            'S': '46',
            'M': '48',
            'S-M': '46;48',
            'L': '50;52',
            'XL': '52; 54',
            'L-XL': '50;54',
            'XXl': '56; 58'
        },
    }

    try:
        size_rus = sizes_dict[gender][size_eur]
    except Exception:
        size_rus = size_eur

    return size_rus


# Функция перевода текста
def translator(text: str) -> str:
    try:
        translator = Translator()
        translation = translator.translate(text, dest='ru')
        return translation.text
    except Exception:
        return text


# Функция получения курса валют
def get_exchange_rate(base_currency: str, target_currency: str) -> int:
    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'

    try:
        response = requests.get(url)
        data = response.json()
        exchange_rate = data['rates'][target_currency]

    except Exception as e:
        print(f"An error occurred: {e}")
        exchange_rate = 0

    return exchange_rate


# Функция для разделения списка на части по n элементов
def chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
