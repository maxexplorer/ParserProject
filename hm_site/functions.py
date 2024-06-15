import requests

from googletrans import Translator


# Функция для перевода формата цветов H&M в Ozone
def colors_format(value: str) -> str:
    if value == 'ANTHRACITE GREY':
        color = 'светло-серый'
    elif value == 'APRICOT':
        color = 'оранжевый'
    elif value == 'AQUAMARINE':
        color = 'серый'
    elif value == 'ASH':
        color = 'серый'
    elif value == 'BEIGE':
        color = 'бежевый'
    elif value == 'BEIGE GREEN':
        color = 'зеленый'
    elif value == 'BEIGE MARL':
        color = 'бежевый'
    elif value == 'BEIGE-PINK':
        color = 'розовый'
    elif value == 'BERRY':
        color = 'бордовый'
    elif value == 'BLACK':
        color = 'черный'
    elif value == 'BLACK BROWN':
        color = 'коричневый'
    elif value == 'BLACK ECRU':
        color = 'бежевый'
    elif value == 'BLACK GREEN':
        color = 'зеленый'
    elif value == 'BLACK MARL':
        color = 'чёрный'
    elif value == 'BLACK SILVER':
        color = 'серебристый'
    elif value == 'BLACK WHITE':
        color = 'белый'
    elif value == 'BLACK YELLOW':
        color = 'желтый'
    elif value == 'BLACK GOLD':
        color = 'золотой'
    elif value == 'BLUE':
        color = 'синий'
    elif value == 'BLUE MARL':
        color = 'бежевый'
    elif value == 'BLUE BLACK':
        color = 'черный'
    elif value == 'BLUE GREEN':
        color = 'зеленый'
    elif value == 'BLUE GREY':
        color = 'серый'
    elif value == 'BLUE INDIGO':
        color = 'синий'
    elif value == 'BLUE NAVY':
        color = 'синий'
    elif value == 'BLUE WHITE':
        color = 'синий'
    elif value == 'BLUE GREEN':
        color = 'зеленый'
    elif value == 'BLUE GREY':
        color = 'серый'
    elif value == 'BLUES':
        color = 'синий'
    elif value == 'BLUISH':
        color = 'синий'
    elif value == 'BLUISH GREY':
        color = 'серый'
    elif value == 'BONE':
        color = 'белый'
    elif value == 'BONE WHITE':
        color = 'белый'
    elif value == 'BOTTLE':
        color = 'белый'
    elif value == 'BRICK':
        color = 'белый'
    elif value == 'BRIGHT RED':
        color = 'красный'
    elif value == 'BRONZE':
        color = 'светло-коричневый'
    elif value == 'BROWN':
        color = 'коричневый'
    elif value == 'BROWN ORANGE':
        color = 'оранжевый'
    elif value == 'BROWN TAUPE':
        color = 'серый'
    elif value == 'BROWN WHITE':
        color = 'белый'
    elif value == 'BROWNISH TONE':
        color = 'коричневый'
    elif value == 'BURGUNDY':
        color = 'бордовый'
    elif value == 'BURGUNDY RED':
        color = 'бордовый'
    elif value == 'CAMEL':
        color = 'светло-бежевый'
    elif value == 'CAMEL WHITE':
        color = 'белый'
    elif value == 'CAMEL BROWN':
        color = 'коричневый'
    elif value == 'CANVAS':
        color = 'белый'
    elif value == 'CARAMEL':
        color = 'желтый'
    elif value == 'CAVA':
        color = 'белый'
    elif value == 'CHALK PINK':
        color = 'розовый'
    elif value == 'CHARCOAL':
        color = 'белый'
    elif value == 'CHARCOAL GREY':
        color = 'серый'
    elif value == 'CHOCOLATE':
        color = 'шоколадный'
    elif value == 'CHOCOLATE BROWN':
        color = 'коричневый'
    elif value == 'CONTRAST':
        color = 'белый'
    elif value == 'COPPER':
        color = 'желтый'
    elif value == 'CREAM':
        color = 'бежевый'
    elif value == 'DARK BLUE':
        color = 'синий'
    elif value == 'DARK GREY':
        color = 'серый'
    elif value == 'DARK KHAKI':
        color = 'хаки'
    elif value == 'DARK ANTHRACITE':
        color = 'светло-серый'
    elif value == 'DARK BEIGE':
        color = 'бежевый'
    elif value == 'DARK BLUE':
        color = 'синий'
    elif value == 'DARK BROWN':
        color = 'коричневый'
    elif value == 'DARK CAMEL':
        color = 'желтый'
    elif value == 'DARK GREEN':
        color = 'зеленый'
    elif value == 'DARK GREY':
        color = 'серый'
    elif value == 'DARK GREY MARL':
        color = 'серый'
    elif value == 'DARK KHAKI':
        color = 'хаки'
    elif value == 'DARK MAUVE':
        color = 'белый'
    elif value == 'DARK NAVY':
        color = 'синий'
    elif value == 'DARK PINK':
        color = 'розовый'
    elif value == 'DARK RED':
        color = 'красный'
    elif value == 'DARK TAN':
        color = 'бежевый'
    elif value == 'DEEP BLUE':
        color = 'синий'
    elif value == 'DENIM INDIGO':
        color = 'синий'
    elif value == 'DENIM BLUE':
        color = 'голубой'
    elif value == 'DENIM BLUE':
        color = 'синий'
    elif value == 'DUCK BLUE':
        color = 'синий'
    elif value == 'DUCK GREEN':
        color = 'зеленый'
    elif value == 'DUSTY PINK':
        color = 'розовый'
    elif value == 'DUSTY PURPLE':
        color = 'сиреневый'
    elif value == 'ECRU':
        color = 'светло-бежевый'
    elif value == 'ECRU BEIGE':
        color = 'бежевый'
    elif value == 'ECRU BLACK':
        color = 'черный'
    elif value == 'ECRU BLUE':
        color = 'голубой'
    elif value == 'ECRU GREEN':
        color = 'зеленый'
    elif value == 'ECRU MARL':
        color = 'бежевый'
    elif value == 'ECRU MAROON':
        color = 'бежевый'
    elif value == 'ECRU NAVY':
        color = 'синий'
    elif value == 'ECRU WHITE':
        color = 'белый'
    elif value == 'EMERALD':
        color = 'зеленый'
    elif value == 'FADED BLACK':
        color = 'черный'
    elif value == 'FADED BLUE':
        color = 'голубой'
    elif value == 'FADED GREEN':
        color = 'зеленый'
    elif value == 'FADED NAVY':
        color = 'синий'
    elif value == 'FADED PINK':
        color = 'розовый'
    elif value == 'FUCHSIA':
        color = 'перламутровый'
    elif value == 'GOLD':
        color = 'золотой'
    elif value == 'GOLDEN':
        color = 'золотой'
    elif value == 'GREEN':
        color = 'зеленый'
    elif value == 'GREEN MARL':
        color = 'белый'
    elif value == 'GREEN BLUE':
        color = 'голубой'
    elif value == 'GREEN ECRU':
        color = 'бежевый'
    elif value == 'GREENISH':
        color = 'зеленый'
    elif value == 'GREY':
        color = 'серый'
    elif value == 'GREY MARL':
        color = 'серый'
    elif value == 'GREY SHADES':
        color = 'серый'
    elif value == 'GREY BEIGE':
        color = 'серый'
    elif value == 'GREY NATURAL':
        color = 'серый'
    elif value == 'GREYGREEN':
        color = 'зеленый'
    elif value == 'GREYISH':
        color = 'серый'
    elif value == 'GREYMARL':
        color = 'серый'
    elif value == 'ICE':
        color = 'светло-синий'
    elif value == 'INDIGO':
        color = 'светло-синий'
    elif value == 'INK BLUE':
        color = 'синий'
    elif value == 'IVORY':
        color = 'бежевый'
    elif value == 'IVORY WHITE':
        color = 'белый'
    elif value == 'JEANS':
        color = 'голубой'
    elif value == 'KHAKI':
        color = 'хаки'
    elif value == 'KHAKI GREEN':
        color = 'зеленый'
    elif value == 'KHAKI MARL':
        color = 'хаки'
    elif value == 'LEOPARD':
        color = 'желтый'
    elif value == 'LIGHT BEIGE':
        color = 'светло-бежевый'
    elif value == 'LIGHT BLUE':
        color = 'синий'
    elif value == 'LIGHT BROWN':
        color = 'коричневый'
    elif value == 'LIGHT CAMEL':
        color = 'желтый'
    elif value == 'LIGHTE CRU':
        color = 'светло-бежевый'
    elif value == 'LIGHT GREEN':
        color = 'светло-зеленый'
    elif value == 'LIGHT GREY':
        color = 'светло-серый'
    elif value == 'LIGHT KHAKI':
        color = 'хаки'
    elif value == 'LIGHT LIME GREEN':
        color = 'зеленый'
    elif value == 'LIGHT MINK':
        color = 'белый'
    elif value == 'LIGHT PINK':
        color = 'светло-розовый'
    elif value == 'LIGHT TAN':
        color = 'желтый'
    elif value == 'LIGHT YELLOW':
        color = 'желтый'
    elif value == 'LILAC':
        color = 'сиреневый'
    elif value == 'LILAC WHITE':
        color = 'белый'
    elif value == 'LIME':
        color = 'желтый'
    elif value == 'MAROON':
        color = 'бордовый'
    elif value == 'MAROON GREY':
        color = 'серый'
    elif value == 'MAUVE':
        color = 'сиреневый'
    elif value == 'MEDIUM BLUE':
        color = 'синий'
    elif value == 'MEDIUM ECRU':
        color = 'бежевый'
    elif value == 'MEDIUM GREY':
        color = 'серый'
    elif value == 'MEDIUM BROWN':
        color = 'коричневый'
    elif value == 'MID-BLUE':
        color = 'светло-синий'
    elif value == 'MID-CAMEL':
        color = 'желтый'
    elif value == 'MID-ECRU':
        color = 'бежевый'
    elif value == 'MID-GREEN':
        color = 'зеленый'
    elif value == 'MID-GREY':
        color = 'серый'
    elif value == 'MID KHAKI':
        color = 'хаки'
    elif value == 'MIDNIGHT BLUE':
        color = 'голубой'
    elif value == 'MID-PINK':
        color = 'розовый'
    elif value == 'MID-TURQUOISE':
        color = 'голубой'
    elif value == 'MINK':
        color = 'бежевый'
    elif value == 'MINK MARL':
        color = 'белый'
    elif value == 'MINT':
        color = 'светло-зеленый'
    elif value == 'MOLE BROWN':
        color = 'коричневый'
    elif value == 'MOSS':
        color = 'зеленый'
    elif value == 'MOSS GREEN':
        color = 'зеленый'
    elif value == 'MUL BERRY':
        color = 'фуксия'
    elif value == 'MULTICOLOURED':
        color = 'разноцветный'
    elif value == 'MUSTARD':
        color = 'горчичный'
    elif value == 'NAVY':
        color = 'голубой'
    elif value == 'NAVY WHITE':
        color = 'белый'
    elif value == 'NAVY BLUE':
        color = 'темно-синий'
    elif value == 'OCHRE':
        color = 'коричневый'
    elif value == 'OFF PINK':
        color = 'розовый'
    elif value == 'OFF WHITE':
        color = 'белый'
    elif value == 'OIL':
        color = 'оливковый'
    elif value == 'OLIVE GREEN':
        color = 'оливковый'
    elif value == 'ONLY ONE':
        color = 'розовый'
    elif value == 'ORANGE':
        color = 'оранжевый'
    elif value == 'ORANGES':
        color = 'оранжевый'
    elif value == 'OYSTE RWHITE':
        color = 'белый'
    elif value == 'PALE BLUE':
        color = 'синий'
    elif value == 'PALE GREY':
        color = 'серый'
    elif value == 'PALE INDIGO':
        color = 'синий'
    elif value == 'PALE KHAKI':
        color = 'хаки'
    elif value == 'PALE MARL':
        color = 'белый'
    elif value == 'PALE OCHRE':
        color = 'оранжевый'
    elif value == 'PALE PINK':
        color = 'розовый'
    elif value == 'PASTEL BLUE':
        color = 'голубой'
    elif value == 'PASTEL PINK':
        color = 'розовый'
    elif value == 'PEARL GREY':
        color = 'светло-серый'
    elif value == 'PETROL BLUE':
        color = 'голубой'
    elif value == 'PINK':
        color = 'розовый'
    elif value == 'PINK LILAC':
        color = 'розовый'
    elif value == 'PINK MARL':
        color = 'розовый'
    elif value == 'PISTACHIO':
        color = 'светло-зеленый'
    elif value == 'PRINT 1':
        color = 'белый'
    elif value == 'PRINTED':
        color = 'белый'
    elif value == 'PURPLE':
        color = 'фиолетовый'
    elif value == 'RED':
        color = 'красный'
    elif value == 'REDDISH':
        color = 'красный'
    elif value == 'RUSSET':
        color = 'коричневый'
    elif value == 'RUST':
        color = 'коричневый'
    elif value == 'SAND':
        color = 'светло-бежевый'
    elif value == 'SAND BROWN':
        color = 'коричневый'
    elif value == 'SAND MARL':
        color = 'бежевый'
    elif value == 'SAND ROWN':
        color = 'коричневый'
    elif value == 'SEA GREEN':
        color = 'светло-синий'
    elif value == 'SILVER':
        color = 'серебристый'
    elif value == 'SKY BLUE':
        color = 'голубой'
    elif value == 'STONE':
        color = 'серый'
    elif value == 'STRAW':
        color = 'белый'
    elif value == 'STRIPED':
        color = 'белый'
    elif value == 'STRIPES':
        color = 'белый'
    elif value == 'TAN GREY':
        color = 'серый'
    elif value == 'TANGERINE':
        color = 'оранжевый'
    elif value == 'TAN MARL':
        color = 'белый'
    elif value == 'TAUPE':
        color = 'белый'
    elif value == 'TAUPE GREY':
        color = 'серый'
    elif value == 'TERRACOTTA':
        color = 'белый'
    elif value == 'TOBACCO BROWN':
        color = 'коричневый'
    elif value == 'TOFFEE':
        color = 'светло-коричневый'
    elif value == 'TURQUOISE':
        color = 'бирюзовый'
    elif value == 'VANILLA':
        color = 'светло-бежевый'
    elif value == 'WASHED PETROL':
        color = 'белый'
    elif value == 'WATER BLUE':
        color = 'синий'
    elif value == 'WHISKY YELLOW':
        color = 'желтый'
    elif value == 'WHITE':
        color = 'белый'
    elif value == 'WHITE NAVY':
        color = 'белый'
    elif value == 'WINE':
        color = 'бордовый'
    elif value == 'YELLOW':
        color = 'желтый'
    elif value == 'WHITE RED':
        color = 'белый'
    elif value == 'WHITE BLACK':
        color = 'белый'
    elif value == 'CORAL':
        color = 'разноцветный'
    elif value == 'TRANSPARENT':
        olor = 'белый'
    elif value == 'BEIGE-T':
        color = 'бежевый'
    elif value == 'MEDIUM GREEN':
        color = 'зеленый'
    elif value == 'GREEN GREY':
        color = 'серый'
    elif value == 'BLUISH GREEN':
        color = 'зеленый'
    elif value == 'BUTTER':
        color = 'бежевый'
    elif value == 'PLUM':
        color = 'фиолетовый'
    elif value == 'STEEL BLUE':
        color = 'синий'
    elif value == 'SNAKESKIN PRINT':
        color = 'черно-серый'
    elif value == 'AUBERGINE':
        color = 'фиолетовый'
    elif value == 'LEAD':
        color = 'черный'
    elif value == 'ECRU KHAKI':
        color = 'хаки'
    elif value == 'CEMENT':
        color = 'серый'
    elif value == 'OLIVE':
        color = 'оливковый'
    elif value == 'OCEAN':
        color = 'синий'
    elif value == 'PASTEL YELLOW':
        color = 'желтый'
    elif value == 'CHEWING GUM':
        color = 'розовый'
    elif value == 'PINK SHADES':
        color = 'розовый'
    elif value == 'WHITE GREY':
        color = 'белый'
    elif value == 'SAND KHAKI':
        color = 'хаки'
    elif value == 'BOTTLE GREEN-T':
        color = 'зеленый'
    elif value == 'BRIGHT WHITE':
        color = 'белый'
    elif value == 'SAND BLUE':
        color = 'синий'
    elif value == 'PEACH':
        color = 'оранжевый'
    elif value == 'ECRU YELLOW':
        color = 'желтый'
    elif value == 'PALE LILAC':
        color = 'светло-розовый'
    elif value == 'BLUE SHADES':
        color = 'синий'
    elif value == 'DARK YARN':
        color = 'коричневый'
    elif value == 'BLACK-BROWN':
        color = 'коричневый'
    elif value == 'FADED SKY BLUE':
        color = 'голубой'
    elif value == 'MEDIUM KHAKI':
        color = 'хаки'
    elif value == 'APPLE GREEN':
        color = 'зеленый'
    elif value == 'NUDE':
        color = 'прозрачный'
    elif value == 'ANTHRACITE KHAKI':
        color = 'хаки'
    elif value == 'PALE ECRU':
        color = 'бежевый'
    elif value == 'LAVENDER':
        color = 'фиолетовый'
    elif value == 'INDIGO BLUE':
        color = 'синий'
    elif value == 'GREENISH BLUE':
        color = 'зеленый'
    elif value == 'RED NAVY':
        color = 'красный'
    elif value == 'BEIGE BROWN':
        color = 'коричневый'
    elif value == 'BLUISH NAVY':
        color = 'голубой'
    elif value == 'SPECKLED MAUVE':
        color = 'серый'
    elif value == 'NATURAL GREY':
        color = 'серый'
    elif value == 'MEDIUM MARL':
        color = 'серый'
    elif value == 'YARN':
        color = 'светло-серый'
    elif value == 'DEEP GREEN':
        color = 'зеленый'
    elif value == 'DARK OCHRE':
        color = 'коричневый'
    elif value == 'DARK MULBERRY':
        color = 'синий'
    elif value == 'DARK MARL':
        color = 'светло-серый'
    elif value == 'LEATHER':
        color = 'коричневый'
    elif value == 'GREY BLUE':
        color = 'зеленый'
    elif value == 'NEON BLUE':
        color = 'синий'
    elif value == 'RASPBERRY':
        color = 'розовый'
    elif value == 'PALE STONE GREY':
        color = 'серый'
    elif value == 'LAVENDER BLUE':
        color = 'синий'
    elif value == 'PALE GREEN':
        color = 'зеленый'
    elif value == 'BROWN-T':
        color = 'коричневый'
    elif value == 'STRAWBERRY':
        color = 'розовый'
    elif value == 'BLUISH TONE':
        color = 'голубой'
    elif value == 'PALE PURPLE':
        color = 'фиолетовый'
    elif value == 'VARIOUS':
        color = 'коричневый'
    elif value == 'LAGOON GREEN':
        color = 'зеленый'
    elif value == 'PEARL MARL':
        color = 'серый'
    elif value == 'PETROLEUM':
        color = 'серый'
    elif value == 'PASTEL GREEN':
        color = 'зеленый'
    elif value == 'PALE BROWN':
        color = 'коричневый'
    elif value == 'CLAY':
        color = 'коричневый'
    elif value == 'ROSE PINK':
        color = 'розовый'
    elif value == 'GREEN / GREY':
        color = 'серый'
    elif value == 'ECRU/WHITE':
        color = 'белый'
    elif value == 'ECRU/KHAKI':
        color = 'хаки'
    elif value == 'DARK MAROON':
        color = 'коричневый'
    elif value == 'LILAC PINK':
        color = 'розовый'
    elif value == 'WHITE/BLACK':
        color = 'белый'
    elif value == 'ECRU/NAVY':
        color = 'черный'
    elif value == 'WHITE/GREY':
        color = 'белый'
    elif value == 'SAND/KHAKI':
        color = 'хаки'
    elif value == 'BLUE/WHITE':
        color = 'белый'
    elif value == 'SAND/BLUE':
        color = 'голубой'
    elif value == 'WHITE/RED':
        color = 'белый'
    elif value == 'ECRU/YELLOW':
        color = 'желтый'
    elif value == 'BEIGE / GREEN':
        color = 'зеленый'
    elif value == 'BROWN/WHITE':
        color = 'коричневый'
    elif value == 'GREY/BLUE':
        color = 'серый'
    elif value == 'ECRU/GREEN':
        color = 'зеленый'
    elif value == 'GREEN/ECRU':
        color = 'зеленый'
    elif value == 'ECRU/BLACK':
        color = 'черный'
    elif value == 'ECRU/BLUE':
        color = 'горлубой'
    elif value == 'BEIGE/BROWN':
        color = 'коричневый'
    elif value == 'ECRU/BEIGE':
        color = 'бежевый'
    elif value == 'RED/NAVY':
        color = 'красный'
    elif value == 'WHITE/NAVY':
        color = 'белый'
    elif value == 'NAVY/WHITE':
        color = 'белый'
    elif value == 'BROWN/ORANGE':
        color = 'коричневый'
    elif value == 'BLACK/ECRU':
        color = 'черный'
    elif value == 'WATER GREEN':
        color = 'зеленый'
    elif value == 'PALE BURGUNDY':
        color = 'бордовый'
    elif value == 'ANTHRACITE/KHAKI':
        color = 'хаки'
    elif value == 'MEDIUM CAMEL':
        color = 'бежевый'
    elif value == 'MULBERRY':
        color = 'серый'
    else:
        color = value
    return color


# Функция для перевода европейских размеров в российские
def get_sizes_format(format: str, gender: str, size_eur: str) -> str:
    sizes_dict = {
        'alpha': {
            'Женщины': {
                'XXS': '40',
                'XS': '42',
                'S': '44',
                'M': '46;48',
                'L': '48;50',
                'M-L': '46;50',
                'XL': '50;52'
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


def get_model_height(category_name: str) -> str:
    if category_name == 'Женщины':
        model_height = '175'
    elif category_name == 'Мужчины':
        model_height = '180'
    else:
        model_height = None

    return model_height


def get_model_size(category_name: str) -> str:
    if category_name == 'Женщины':
        model_size = 'S'
    elif category_name == 'Мужчины':
        model_size = 'M'
    else:
        model_size = None

    return model_size


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
