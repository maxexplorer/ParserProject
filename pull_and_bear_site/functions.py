import requests

from googletrans import Translator


# Функция для перевода формата цветов Pull and Bear в Ozone
def colors_format(value: str) -> str:
    match value:
        case 'ANTHRACITE GREY':
            color = 'светло-серый'
        case 'APRICOT':
            color = 'оранжевый'
        case 'AQUAMARINE':
            color = 'серый'
        case 'ASH':
            color = 'серый'
        case 'BEIGE':
            color = 'бежевый'
        case 'BEIGE GREEN':
            color = 'зеленый'
        case 'BEIGE MARL':
            color = 'бежевый'
        case 'BEIGE-PINK':
            color = 'розовый'
        case 'BERRY':
            color = 'бордовый'
        case 'BLACK':
            color = 'черный'
        case 'BLACK BROWN':
            color = 'коричневый'
        case 'BLACK ECRU':
            color = 'бежевый'
        case 'BLACK GREEN':
            color = 'зеленый'
        case 'BLACK MARL':
            color = 'чёрный'
        case 'BLACK SILVER':
            color = 'серебристый'
        case 'BLACK WHITE':
            color = 'белый'
        case 'BLACK YELLOW':
            color = 'желтый'
        case 'BLACK GOLD':
            color = 'золотой'
        case 'BLUE':
            color = 'синий'
        case 'BLUE MARL':
            color = 'бежевый'
        case 'BLUE BLACK':
            color = 'черный'
        case 'BLUE GREEN':
            color = 'зеленый'
        case 'BLUE GREY':
            color = 'серый'
        case 'BLUE INDIGO':
            color = 'синий'
        case 'BLUE NAVY':
            color = 'синий'
        case 'BLUE WHITE':
            color = 'синий'
        case 'BLUE GREEN':
            color = 'зеленый'
        case 'BLUE GREY':
            color = 'серый'
        case 'BLUES':
            color = 'синий'
        case 'BLUISH':
            color = 'синий'
        case 'BLUISH GREY':
            color = 'серый'
        case 'BONE':
            color = 'белый'
        case 'BONE WHITE':
            color = 'белый'
        case 'BOTTLE':
            color = 'белый'
        case 'BRICK':
            color = 'белый'
        case 'BRIGHT RED':
            color = 'красный'
        case 'BRONZE':
            color = 'светло-коричневый'
        case 'BROWN':
            color = 'коричневый'
        case 'BROWN ORANGE':
            color = 'оранжевый'
        case 'BROWN TAUPE':
            color = 'серый'
        case 'BROWN WHITE':
            color = 'белый'
        case 'BROWNISH TONE':
            color = 'коричневый'
        case 'BURGUNDY':
            color = 'бордовый'
        case 'BURGUNDY RED':
            color = 'бордовый'
        case 'CAMEL':
            color = 'светло-бежевый'
        case 'CAMEL WHITE':
            color = 'белый'
        case 'CAMEL BROWN':
            color = 'коричневый'
        case 'CANVAS':
            color = 'белый'
        case 'CARAMEL':
            color = 'желтый'
        case 'CAVA':
            color = 'белый'
        case 'CHALK PINK':
            color = 'розовый'
        case 'CHARCOAL':
            color = 'белый'
        case 'CHARCOAL GREY':
            color = 'серый'
        case 'CHOCOLATE':
            color = 'шоколадный'
        case 'CHOCOLATE BROWN':
            color = 'коричневый'
        case 'CONTRAST':
            color = 'белый'
        case 'COPPER':
            color = 'желтый'
        case 'CREAM':
            color = 'бежевый'
        case 'DARK BLUE':
            color = 'синий'
        case 'DARK GREY':
            color = 'серый'
        case 'DARK KHAKI':
            color = 'хаки'
        case 'DARK ANTHRACITE':
            color = 'светло-серый'
        case 'DARK BEIGE':
            color = 'бежевый'
        case 'DARK BLUE':
            color = 'синий'
        case 'DARK BROWN':
            color = 'коричневый'
        case 'DARK CAMEL':
            color = 'желтый'
        case 'DARK GREEN':
            color = 'зеленый'
        case 'DARK GREY':
            color = 'серый'
        case 'DARK GREY MARL':
            color = 'серый'
        case 'DARK KHAKI':
            color = 'хаки'
        case 'DARK MAUVE':
            color = 'белый'
        case 'DARK NAVY':
            color = 'синий'
        case 'DARK PINK':
            color = 'розовый'
        case 'DARK RED':
            color = 'красный'
        case 'DARK TAN':
            color = 'бежевый'
        case 'DEEP BLUE':
            color = 'синий'
        case 'DENIM INDIGO':
            color = 'синий'
        case 'DENIM BLUE':
            color = 'голубой'
        case 'DENIM BLUE':
            color = 'синий'
        case 'DUCK BLUE':
            color = 'синий'
        case 'DUCK GREEN':
            color = 'зеленый'
        case 'DUSTY PINK':
            color = 'розовый'
        case 'DUSTY PURPLE':
            color = 'сиреневый'
        case 'ECRU':
            color = 'светло-бежевый'
        case 'ECRU BEIGE':
            color = 'бежевый'
        case 'ECRU BLACK':
            color = 'черный'
        case 'ECRU BLUE':
            color = 'голубой'
        case 'ECRU GREEN':
            color = 'зеленый'
        case 'ECRU MARL':
            color = 'бежевый'
        case 'ECRU MAROON':
            color = 'бежевый'
        case 'ECRU NAVY':
            color = 'синий'
        case 'ECRU WHITE':
            color = 'белый'
        case 'EMERALD':
            color = 'зеленый'
        case 'FADED BLACK':
            color = 'черный'
        case 'FADED BLUE':
            color = 'голубой'
        case 'FADED GREEN':
            color = 'зеленый'
        case 'FADED NAVY':
            color = 'синий'
        case 'FADED PINK':
            color = 'розовый'
        case 'FUCHSIA':
            color = 'перламутровый'
        case 'GOLD':
            color = 'золотой'
        case 'GOLDEN':
            color = 'золотой'
        case 'GREEN':
            color = 'зеленый'
        case 'GREEN MARL':
            color = 'белый'
        case 'GREEN BLUE':
            color = 'голубой'
        case 'GREEN ECRU':
            color = 'бежевый'
        case 'GREENISH':
            color = 'зеленый'
        case 'GREY':
            color = 'серый'
        case 'GREY BLUE':
            color = 'синий'
        case 'GREY MARL':
            color = 'серый'
        case 'GREY SHADES':
            color = 'серый'
        case 'GREY BEIGE':
            color = 'серый'
        case 'GREY BLUE':
            color = 'серый'
        case 'GREY NATURAL':
            color = 'серый'
        case 'GREYGREEN':
            color = 'зеленый'
        case 'GREYISH':
            color = 'серый'
        case 'GREYMARL':
            color = 'серый'
        case 'ICE':
            color = 'светло-синий'
        case 'INDIGO':
            color = 'светло-синий'
        case 'INKBLUE':
            color = 'синий'
        case 'IVORY':
            color = 'бежевый'
        case 'IVORYWHITE':
            color = 'белый'
        case 'JEANS':
            color = 'голубой'
        case 'KHAKI':
            color = 'хаки'
        case 'KHAKIGREEN':
            color = 'зеленый'
        case 'KHAKIMARL':
            color = 'хаки'
        case 'LEOPARD':
            color = 'желтый'
        case 'LIGHTBEIGE':
            color = 'светло-бежевый'
        case 'LIGHTBLUE':
            color = 'синий'
        case 'LIGHTBROWN':
            color = 'коричневый'
        case 'LIGHTCAMEL':
            color = 'желтый'
        case 'LIGHTECRU':
            color = 'светло-бежевый'
        case 'LIGHTGREEN':
            color = 'светло-зеленый'
        case 'LIGHTGREY':
            color = 'светло-серый'
        case 'LIGHTKHAKI':
            color = 'хаки'
        case 'LIGHTLIMEGREEN':
            color = 'зеленый'
        case 'LIGHTMINK':
            color = 'белый'
        case 'LIGHTPINK':
            color = 'светло-розовый'
        case 'LIGHTTAN':
            color = 'желтый'
        case 'LIGHTYELLOW':
            color = 'желтый'
        case 'LILAC':
            color = 'сиреневый'
        case 'LILAC WHITE':
            color = 'белый'
        case 'LIME':
            color = 'желтый'
        case 'MAROON':
            color = 'бордовый'
        case 'MAROONGREY':
            color = 'серый'
        case 'MAUVE':
            color = 'сиреневый'
        case 'MEDIUM BLUE':
            color = 'синий'
        case 'MEDIUM ECRU':
            color = 'бежевый'
        case 'MEDIUM GREY':
            color = 'серый'
        case 'MEDIUMBROWN':
            color = 'коричневый'
        case 'MID-BLUE':
            color = 'светло-синий'
        case 'MID-CAMEL':
            color = 'желтый'
        case 'MID-ECRU':
            color = 'бежевый'
        case 'MID-GREEN':
            color = 'зеленый'
        case 'MID-GREY':
            color = 'серый'
        case 'MIDKHAKI':
            color = 'хаки'
        case 'MIDNIGHTBLUE':
            color = 'голубой'
        case 'MID-PINK':
            color = 'розовый'
        case 'MID-TURQUOISE':
            color = 'голубой'
        case 'MINK':
            color = 'бежевый'
        case 'MINKMARL':
            color = 'белый'
        case 'MINT':
            color = 'светло-зеленый'
        case 'MOLE BROWN':
            color = 'коричневый'
        case 'MOSS':
            color = 'зеленый'
        case 'MOSSGREEN':
            color = 'зеленый'
        case 'MULBERRY':
            color = 'фуксия'
        case 'MULTICOLOURED':
            color = 'разноцветный'
        case 'MUSTARD':
            color = 'горчичный'
        case 'NAVY':
            color = 'голубой'
        case 'NAVY WHITE':
            color = 'белый'
        case 'NAVYBLUE':
            color = 'темно-синий'
        case 'OCHRE':
            color = 'коричневый'
        case 'OFF PINK':
            color = 'розовый'
        case 'OFF WHITE':
            color = 'белый'
        case 'OIL':
            color = 'оливковый'
        case 'OLIVEGREEN':
            color = 'оливковый'
        case 'ONLYONE':
            color = 'розовый'
        case 'ORANGE':
            color = 'оранжевый'
        case 'ORANGES':
            color = 'оранжевый'
        case 'OYSTERWHITE':
            color = 'белый'
        case 'PALE BLUE':
            color = 'синий'
        case 'PALE GREY':
            color = 'серый'
        case 'PALE INDIGO':
            color = 'синий'
        case 'PALE KHAKI':
            color = 'хаки'
        case 'PALE MARL':
            color = 'белый'
        case 'PALE OCHRE':
            color = 'оранжевый'
        case 'PALEPINK':
            color = 'розовый'
        case 'PALEPINK':
            color = 'розовый'
        case 'PASTEL BLUE':
            color = 'голубой'
        case 'PASTELPINK':
            color = 'розовый'
        case 'PEARLGREY':
            color = 'светло-серый'
        case 'PETROLBLUE':
            color = 'голубой'
        case 'PINK':
            color = 'розовый'
        case 'PINK LILAC':
            color = 'розовый'
        case 'PINKMARL':
            color = 'розовый'
        case 'PISTACHIO':
            color = 'светло-зеленый'
        case 'PRINT 1':
            color = 'белый'
        case 'PRINTED':
            color = 'белый'
        case 'PURPLE':
            color = 'фиолетовый'
        case 'RED':
            color = 'красный'
        case 'REDDISH':
            color = 'красный'
        case 'RUSSET':
            color = 'коричневый'
        case 'RUST':
            color = 'коричневый'
        case 'SAND':
            color = 'светло-бежевый'
        case 'SAND BROWN':
            color = 'коричневый'
        case 'SAND MARL':
            color = 'бежевый'
        case 'SANDBROWN':
            color = 'коричневый'
        case 'SEAGREEN':
            color = 'светло-синий'
        case 'SILVER':
            color = 'серебристый'
        case 'SKYBLUE':
            color = 'голубой'
        case 'STONE':
            color = 'серый'
        case 'STRAW':
            color = 'белый'
        case 'STRIPED':
            color = 'белый'
        case 'STRIPES':
            color = 'белый'
        case 'TAN GREY':
            color = 'серый'
        case 'TANGERINE':
            color = 'оранжевый'
        case 'TANMARL':
            color = 'белый'
        case 'TAUPE':
            color = 'белый'
        case 'TAUPEGREY':
            color = 'серый'
        case 'TERRACOTTA':
            color = 'белый'
        case 'TOBACCO BROWN':
            color = 'коричневый'
        case 'TOFFEE':
            color = 'светло-коричневый'
        case 'TURQUOISE':
            color = 'бирюзовый'
        case 'VANILLA':
            color = 'светло-бежевый'
        case 'WASHEDPETROL':
            color = 'белый'
        case 'WATER BLUE':
            color = 'синий'
        case 'WHISKYYELLOW':
            color = 'желтый'
        case 'WHITE':
            color = 'белый'
        case 'WHITE NAVY':
            color = 'белый'
        case 'WINE':
            color = 'бордовый'
        case 'YELLOW':
            color = 'желтый'
        case _:
            color = value

    return color


# Функция для перевода европейских размеров в российские
def sizes_format(format: str, gender: str, size_eur: str) -> str:
    sizes_dict = {
        'alpha': {
            'WOMEN': {
                'XXS': '40',
                'XS': '42',
                'S': '44',
                'M': '46;48',
                'L': '48;50',
                'M-L': '46;50',
                'XL': '50;52'
            },
            'MAN': {
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
            'WOMEN': {
                '32': '38',
                '34': '40',
                '36': '42',
                '38': '44',
                '40': '46',
                '42': '48',
                '44': '50',
                '46': '52',
                '48': '52'
            },
            'MAN': {
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

    size_rus = sizes_dict[format][gender][size_eur]

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
def get_exchange_rate() -> int:
    base_currency = 'EUR'
    target_currency = 'RUB'

    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'

    try:
        response = requests.get(url)
        data = response.json()
        exchange_rate = data['rates'][target_currency]

    except Exception as e:
        print(f"An error occurred: {e}")
        exchange_rate = 0

    return exchange_rate
