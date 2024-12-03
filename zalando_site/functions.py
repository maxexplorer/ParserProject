import requests

from googletrans import Translator

# Функция для перевода формата цветов H&M в ozon
def colors_format(value: str) -> str:
    if value == 'Schwarz':
        color = 'черный'
    elif value == 'Weiß/Blau geblümt':
        color = 'белый'
    elif value == 'Grün/Gemustert':
        color = 'зеленый'
    elif value == 'Cremefarben/Geblümt':
        color = 'кремовый'
    elif value == 'Cremefarben/Schwarz geblümt':
        color = 'кремовый'
    elif value == 'Graumeliert':
        color = 'серый'
    elif value == 'Hellbeige':
        color = 'бежевый'
    elif value == 'Cremefarben/Zitrone':
        color = 'белый'
    elif value == 'Blassgrünmeliert':
        color = 'зеленый'
    elif value == 'Dunkles Khakigrün':
        color = 'зеленый'
    elif value == 'Hellbeige/Gestreift':
        color = 'бежевый'
    elif value == 'Weiß/Schwarz gestreift':
        color = 'белый'
    elif value == 'Hellbeigemeliert':
        color = 'бежевый'
    elif value == 'Khakigrün':
        color = 'зеленый'
    elif value == 'Schwarz/Geblümt':
        color = 'черный'
    elif value == 'Blau/Gemustert':
        color = 'синий'
    elif value == 'Gelb/Geblümt':
        color = 'желтый'
    elif value == 'Hellrosa/Geblümt':
        color = 'розовый'
    elif value == 'Schwarz/Weiß gestreift':
        color = 'черный'
    elif value == 'Schwarz/Gestreift':
        color = 'черный'
    elif value == 'Dark brown':
        color = 'коричневый'
    elif value == 'Blau':
        color = 'синий'
    elif value == 'Weiß/Geblümt':
        color = 'белый'
    elif value == 'Grün/Blattmuster':
        color = 'зеленый'
    elif value == 'Cremefarben':
        color = 'кремовый'
    elif value == 'Hellblau/Gestreift':
        color = 'голубой'
    elif value == 'Hellrosa/Gemustert':
        color = 'розовый'
    elif value == 'Weiß':
        color = 'белый'
    elif value == 'Grün/Geblümt':
        color = 'зеленый'
    elif value == 'Dunkelbeige':
        color = 'бежевый'
    elif value == 'Cremefarben/Gestreift':
        color = 'кремовый'
    elif value == 'Blau/Geblümt':
        color = 'синий'
    elif value == 'Schwarz/Gemustert':
        color = 'черный'
    elif value == 'Cremefarben/Schwarz gestreift':
        color = 'кремовый'
    elif value == 'Dunkelgrau':
        color = 'серый'
    elif value == 'Hellgraumeliert':
        color = 'серый'
    elif value == 'Naturweiß':
        color = 'белый'
    elif value == 'Cremefarben/Schwarz gemustert':
        color = 'кремовый'
    elif value == 'Green/Patterned':
        color = 'зеленый'
    elif value == 'Cremefarben/Blau geblümt':
        color = 'кремовый'
    elif value == 'Naturweiß/Geblümt':
        color = 'белый'
    elif value == 'Helles Greige':
        color = 'серый'
    elif value == 'Beige':
        color = 'бежевый'
    elif value == 'Hellblau':
        color = 'синий'
    elif value == 'Mattgrün':
        color = 'зеленый'
    elif value == 'Dunkelorange/Gemustert':
        color = 'оранжевый'
    elif value == 'Schwarz/Weiß gemustert':
        color = 'черный'
    elif value == 'Weinrot':
        color = 'красный'
    elif value == 'Grün':
        color = 'зеленый'
    elif value == 'Dunkles Taupe':
        color = 'коричневый'
    elif value == 'Schwarz/Batikmuster':
        color = 'черный'
    elif value == 'Black':
        color = 'черный'
    elif value == 'Helles Khakigrün':
        color = 'зеленый'
    elif value == 'Knallrot':
        color = 'красный'
    elif value == 'Blau/Gestreift':
        color = 'синий'
    elif value == 'Marineblau/Gemustert':
        color = 'синий'
    elif value == 'Hellgrau':
        color = 'серый'
    elif value == 'Weiß/Gestreift':
        color = 'белый'
    elif value == 'Cremefarben/Klein geblümt':
        color = 'кремовый'
    elif value == 'Orange/Gemustert':
        color = 'оранжевый'
    elif value == 'Knallblau/Gemustert':
        color = 'синий'
    elif value == 'Weiß/Blau gestreift':
        color = 'белый'
    elif value == 'Hellblau/Geblümt':
        color = 'голубой'
    elif value == 'Weiß/Blau gemustert':
        color = 'белый'
    elif value == 'Hellgrün':
        color = 'зеленый'
    elif value == 'Helles Matttürkis':
        color = 'бирюзовый'
    elif value == 'Rostbraun':
        color = 'коричневый'
    elif value == 'Pistaziengrün':
        color = 'зеленый'
    elif value == 'Flieder':
        color = 'сиреневый'
    elif value == 'Cremefarben/Bäume':
        color = 'кремовый'
    elif value == 'Cremefarben/Grün gemustert':
        color = 'кремовый'
    elif value == 'Blau/Batikmuster':
        color = 'синий'
    elif value == 'Blau/Weiß gestreift':
        color = 'синий'
    elif value == 'Dunkelgrau/Zebramuster':
        color = 'серый'
    elif value == 'Cremefarben/Beige gemustert':
        color = 'кремовый'
    elif value == 'Puderrosa':
        color = 'розовый'
    elif value == 'Cremefarben/Rot gemustert':
        color = 'кремовый'
    elif value == 'Dunkelbraun':
        color = 'коричневый'
    elif value == 'Weiss/Gemustert':
        color = 'белый'
    elif value == 'Cremefarben/Batikmuster':
        color = 'кремовый'
    elif value == 'Dunkelblau/Gemustert':
        color = 'синий'
    elif value == 'Beige/Leopardenprint':
        color = 'бежевый'
    elif value == 'Cremefarben/Blau gestreift':
        color = 'кремовый'
    elif value == 'White/Floral':
        color = 'белый'
    elif value == 'Türkis/Gemustert':
        color = 'бирюзовый'
    elif value == 'Navy blue':
        color = 'синий'
    elif value == 'Cremefarben/Rosen':
        color = 'кремовый'
    elif value == 'Marineblau/Gestreift':
        color = 'синий'
    elif value == 'Weißes Blumenmuster auf Rot':
        color = 'белый'
    elif value == 'Weiß/Gemustert':
        color = 'белый'
    elif value == 'Blassrosa':
        color = 'белый'
    elif value == 'Weiss/Rot gemustert':
        color = 'белый'
    elif value == 'Blaugrau':
        color = 'белый'
    elif value == 'Weiß/Geblümt':
        color = 'белый'
    elif value == 'Beige/Schlangenmuster':
        color = 'бежевый'
    elif value == 'Hellbeige/Zebraprint':
        color = 'бежевый'
    elif value == 'Dunkles Graubraun':
        color = 'коричневый'
    elif value == 'Basic Schwarz':
        color = 'черный'
    elif value == 'Weiß/Schwarz':
        color = 'белый'
    elif value == 'Weiß/Blauer Blumenprint':
        color = 'синий'
    elif value == 'Beige bedruckt':
        color = 'бежевый'
    elif value == 'Blauer Denim':
        color = 'белый'
    elif value == 'Leuchtend Rot':
        color = 'красный'
    elif value == 'Beige/Flieder':
        color = 'бежевый'
    elif value == 'Blue':
        color = 'синий'
    elif value == 'Beige/Weiß':
        color = 'бежевый'
    elif value == 'Helles Taupe':
        color = 'серый'
    elif value == 'Green':
        color = 'зеленый'
    elif value == 'Amethyst':
        color = 'серый'
    elif value == 'Blau/Paisleymuster':
        color = 'белый'
    elif value == 'White':
        color = 'белый'
    elif value == 'Weiß/Schwarzer Blumenprint':
        color = 'белый'
    elif value == 'Weiß/Blumendruck':
        color = 'белый'
    elif value == 'Weiß/Marineblau gestreift':
        color = 'белый'
    elif value == 'Weiß/Micky Maus':
        color = 'белый'
    elif value == 'Weiß/Hellblau gestreift':
        color = 'белый'
    elif value == 'Weiß/Blau geblümt':
        color = 'белый'
    elif value == 'White/Alle Stelle!':
        color = 'белый'
    elif value == 'Blassgelb':
        color = 'бежевый'
    elif value == 'Weiß/Rot gestreift':
        color = 'белый'
    elif value == 'Weiß/Taupe gestreift':
        color = 'белый'
    elif value == 'Weiß/NFL':
        color = 'белый'
    elif value == "Weiß/Guns N' Roses":
        color = 'белый'
    elif value == 'Beige/Gestreift':
        color = 'бежевый'
    elif value == 'Weiß/Biarritz':
        color = 'белый'
    elif value == 'Weiß/Biarritz':
        color = 'белый'
    elif value == 'Weiß/Beige gestreift':
        color = 'белый'
    elif value == 'Weiß/Nirvana':
        color = 'белый'
    elif value == 'Weiß/Coca-Cola':
        color = 'белый'
    elif value == 'WEISS/BRAUN':
        color = 'белый'
    elif value == 'Türkis/Ausgewaschen':
        color = 'бирюзовый'
    elif value == 'Beige/Ombre':
        color = 'бежевый'
    elif value == 'Blasses Denimblau':
        color = 'белый'
    elif value == 'Weiß/ Hellbeige gestreift':
        color = 'белый'
    elif value == 'Weiß/ Hellbeige gestreift':
        color = 'белый'
    elif value == 'Weiß/Fender':
        color = 'белый'
    elif value == 'Dark grey':
        color = 'серый'
    elif value == 'Weiß/Germany':
        color = 'белый'
    elif value == 'Weiß/Gepunktet':
        color = 'белый'
    elif value == 'Weiß/Gelb/Blau':
        color = 'белый'
    elif value == 'BEIGE/UNGEFÄRBT':
        color = 'бежевый'
    elif value == 'Blasses Weiß':
        color = 'белый'
    elif value == 'Türkis':
        color = 'бирюзовый'
    elif value == 'Weiß/Santa Monica':
        color = 'белый'
    elif value == 'Dunkles Greige':
        color = 'серый'
    elif value == 'Weiß / Navyblau':
        color = 'белый'
    elif value == 'Weiß/Rot':
        color = 'белый'
    elif value == 'Beige/cremefarben gestreift':
        color = 'бежевый'
    elif value == 'Weiß/Blau':
        color = 'белый'
    elif value == 'Anthrazit':
        color = 'серый'
    elif value == 'Weiße Blumenstickerei':
        color = 'бежевый'
    elif value == 'Weiß/Marineblau':
        color = 'белый'
    elif value == 'White +':
        color = 'белый'
    elif value == 'Weiß/Blume':
        color = 'белый'
    elif value == 'Blau/University':
        color = 'белый'
    elif value == 'Weiß/Schwarz/Cremefarben':
        color = 'белый'
    elif value == 'Beige/Red Hot Chili Peppers':
        color = 'бежевый'
    elif value == 'Petrol':
        color = 'желтый'
    elif value == 'White Cn-100xx':
        color = 'белый'
    elif value == 'Weiß/Beige':
        color = 'белый'
    elif value == 'Weiß mit Print':
        color = 'белый'
    elif value == 'Weiß/Muscheln':
        color = 'белый'
    elif value == 'Weiß//Misfits':
        color = 'белый'
    elif value == 'Beige/Orange':
        color = 'бежевый'
    elif value == 'Weiß/Blau':
        color = 'белый'
    elif value == 'Blassrot':
        color = 'белый'
    elif value == 'Beige/Schwarz/Gestreift':
        color = 'бежевый'
    elif value == 'Weiß/Blockfarben':
        color = 'белый'
    elif value == 'Weiß/Navyblau gestreift':
        color = 'белый'
    elif value == 'Blassblau':
        color = 'белый'
    elif value == 'Weiß/Nadelstreifen':
        color = 'белый'
    elif value == 'WEISS/BOTANISCHER PRINT':
        color = 'белый'
    elif value == 'Weiß/Perlen':
        color = 'белый'
    elif value == 'Blau/weiße Streifen':
        color = 'синий'
    elif value == 'Weiß/Beige/Flieder':
        color = 'белый'
    elif value == 'Weiß/Beige/Flieder':
        color = 'белый'
    elif value == 'Weiß/Palmenblätter':
        color = 'белый'
    elif value == 'Weiss/Gestreift':
        color = 'белый'
    elif value == 'Weiß/Grau':
        color = 'белый'
    elif value == 'Beige/Blauer Blumenprint':
        color = 'бежевый'
    elif value == 'Light greige':
        color = 'серый'
    elif value == 'Light beige':
        color = 'бежевый'
    elif value == 'Helles Khakigrün/Batik':
        color = 'зеленый'
    elif value == 'Cooles Blau':
        color = 'синий'
    elif value == 'Blasses Beige':
        color = 'бежевый'
    elif value == 'Weiß/Blumen':
        color = 'белый'
    elif value == 'Beige/khaki':
        color = 'бежевый'
    elif value == 'Dark Blue Unwashed':
        color = 'синий'
    elif value == 'Weiß/Schwarz meliert':
        color = 'белый'
    elif value == 'Beige kariert':
        color = 'бежевый'
    elif value == 'Weiß/Lila geblümt':
        color = 'белый'
    elif value == 'Hellgraumeliert/Schwarz':
        color = 'серый'
    elif value == 'Hellgrau/Schwarz':
        color = 'серый'
    elif value == 'Cacao':
        color = 'коричневый'
    elif value == 'Black Worn In':
        color = 'черный'
    elif value == 'Light Indigo - Worn In':
        color = 'синий'
    elif value == 'Korallenrot/Geblümt':
        color = 'красный'
    elif value == 'Helles Khakigrün/Schwarz':
        color = 'зеленый'
    else:
        color = value
    return color


# Функция для перевода европейских размеров в российские
def sizes_format(format: str, gender: str, size_eur: str) -> str:
    sizes_dict = {
        'alpha': {
            'Женщины': {
                '2XS': '36;38',
                'XXS': '40',
                'XS': '42',
                'S': '44',
                'M': '46;48',
                'L': '48;50',
                'M-L': '46;50',
                'XL': '50;52',
                'XXL': '54'
            },
            'Мужчины': {
                'XS': '44',
                'S': '46',
                'M': '48',
                'S-M': '46;48',
                'L': '50;52',
                'XL': '52; 54',
                'L-XL': '50;54',
                'XXl': '56; 58'
            }
        },
        'digit': {
            'Женщины': {
                '32': '38',
                '34': '40',
                '36': '42',
                '38': '44',
                '40': '46',
                '42': '48',
                '44': '50',
                '46': '52',
                '48': '54'
            },
            'Мужчины': {
                '32': '38',
                '34': '40',
                '36': '42',
                '38': '44',
                '40': '46',
                '42': '48',
                '44': '50',
                '46': '52',
                '48': '54'
            }
        }
    }

    try:
        size_rus = sizes_dict[format][gender][size_eur]
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


def get_unique_urls(file_path: str) -> set:
    # Читаем все URL-адреса из файла и сразу создаем множество для удаления дубликатов
    with open(file_path, 'r', encoding='utf-8') as file:
        unique_urls = set(line.strip() for line in file)

    # Сохраняем уникальные URL-адреса обратно в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        print(*unique_urls, file=file, sep='\n')

    return unique_urls
