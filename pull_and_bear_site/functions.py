import requests

from googletrans import Translator


# Функция для перевода формата цветов Pull and Bear в Ozone
def colors_format_match(value: str) -> str:
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
        case 'GREY MARL':
            color = 'серый'
        case 'GREY SHADES':
            color = 'серый'
        case 'GREY BEIGE':
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
        case 'INK BLUE':
            color = 'синий'
        case 'IVORY':
            color = 'бежевый'
        case 'IVORY WHITE':
            color = 'белый'
        case 'JEANS':
            color = 'голубой'
        case 'KHAKI':
            color = 'хаки'
        case 'KHAKI GREEN':
            color = 'зеленый'
        case 'KHAKI MARL':
            color = 'хаки'
        case 'LEOPARD':
            color = 'желтый'
        case 'LIGHT BEIGE':
            color = 'светло-бежевый'
        case 'LIGHT BLUE':
            color = 'синий'
        case 'LIGHT BROWN':
            color = 'коричневый'
        case 'LIGHT CAMEL':
            color = 'желтый'
        case 'LIGHTE CRU':
            color = 'светло-бежевый'
        case 'LIGHT GREEN':
            color = 'светло-зеленый'
        case 'LIGHT GREY':
            color = 'светло-серый'
        case 'LIGHT KHAKI':
            color = 'хаки'
        case 'LIGHT LIME GREEN':
            color = 'зеленый'
        case 'LIGHT MINK':
            color = 'белый'
        case 'LIGHT PINK':
            color = 'светло-розовый'
        case 'LIGHT TAN':
            color = 'желтый'
        case 'LIGHT YELLOW':
            color = 'желтый'
        case 'LILAC':
            color = 'сиреневый'
        case 'LILAC WHITE':
            color = 'белый'
        case 'LIME':
            color = 'желтый'
        case 'MAROON':
            color = 'бордовый'
        case 'MAROON GREY':
            color = 'серый'
        case 'MAUVE':
            color = 'сиреневый'
        case 'MEDIUM BLUE':
            color = 'синий'
        case 'MEDIUM ECRU':
            color = 'бежевый'
        case 'MEDIUM GREY':
            color = 'серый'
        case 'MEDIUM BROWN':
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
        case 'MID KHAKI':
            color = 'хаки'
        case 'MIDNIGHT BLUE':
            color = 'голубой'
        case 'MID-PINK':
            color = 'розовый'
        case 'MID-TURQUOISE':
            color = 'голубой'
        case 'MINK':
            color = 'бежевый'
        case 'MINK MARL':
            color = 'белый'
        case 'MINT':
            color = 'светло-зеленый'
        case 'MOLE BROWN':
            color = 'коричневый'
        case 'MOSS':
            color = 'зеленый'
        case 'MOSS GREEN':
            color = 'зеленый'
        case 'MUL BERRY':
            color = 'фуксия'
        case 'MULTICOLOURED':
            color = 'разноцветный'
        case 'MUSTARD':
            color = 'горчичный'
        case 'NAVY':
            color = 'голубой'
        case 'NAVY WHITE':
            color = 'белый'
        case 'NAVY BLUE':
            color = 'темно-синий'
        case 'OCHRE':
            color = 'коричневый'
        case 'OFF PINK':
            color = 'розовый'
        case 'OFF WHITE':
            color = 'белый'
        case 'OIL':
            color = 'оливковый'
        case 'OLIVE GREEN':
            color = 'оливковый'
        case 'ONLY ONE':
            color = 'розовый'
        case 'ORANGE':
            color = 'оранжевый'
        case 'ORANGES':
            color = 'оранжевый'
        case 'OYSTE RWHITE':
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
        case 'PALE PINK':
            color = 'розовый'
        case 'PASTEL BLUE':
            color = 'голубой'
        case 'PASTEL PINK':
            color = 'розовый'
        case 'PEARL GREY':
            color = 'светло-серый'
        case 'PETROL BLUE':
            color = 'голубой'
        case 'PINK':
            color = 'розовый'
        case 'PINK LILAC':
            color = 'розовый'
        case 'PINK MARL':
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
        case 'SAND ROWN':
            color = 'коричневый'
        case 'SEA GREEN':
            color = 'светло-синий'
        case 'SILVER':
            color = 'серебристый'
        case 'SKY BLUE':
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
        case 'TAN MARL':
            color = 'белый'
        case 'TAUPE':
            color = 'белый'
        case 'TAUPE GREY':
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
        case 'WASHED PETROL':
            color = 'белый'
        case 'WATER BLUE':
            color = 'синий'
        case 'WHISKY YELLOW':
            color = 'желтый'
        case 'WHITE':
            color = 'белый'
        case 'WHITE NAVY':
            color = 'белый'
        case 'WINE':
            color = 'бордовый'
        case 'YELLOW':
            color = 'желтый'
        case 'WHITE RED':
            color = 'белый'
        case 'WHITE BLACK':
            color = 'белый'
        case 'CORAL':
            color = 'разноцветный'
        case 'TRANSPARENT':
            color = 'белый'
        case 'BEIGE-T':
            color = 'бежевый'
        case 'MEDIUM GREEN':
            color = 'зеленый'
        case 'GREEN GREY':
            color = 'серый'
        case 'BLUISH GREEN':
            color = 'зеленый'
        case 'BUTTER':
            color = 'бежевый'
        case 'PLUM':
            color = 'фиолетовый'
        case 'STEEL BLUE':
            color = 'синий'
        case 'SNAKESKIN PRINT':
            color = 'черно-серый'
        case 'AUBERGINE':
            color = 'фиолетовый'
        case 'LEAD':
            color = 'черный'
        case 'ECRU KHAKI':
            color = 'хаки'
        case 'CEMENT':
            color = 'серый'
        case 'OLIVE':
            color = 'оливковый'
        case 'OCEAN':
            color = 'синий'
        case 'PASTEL YELLOW':
            color = 'желтый'
        case 'CHEWING GUM':
            color = 'розовый'
        case 'PINK SHADES':
            color = 'розовый'
        case 'WHITE GREY':
            color = 'белый'
        case 'SAND KHAKI':
            color = 'хаки'
        case 'BOTTLE GREEN-T':
            color = 'зеленый'
        case 'BRIGHT WHITE':
            color = 'белый'
        case 'SAND BLUE':
            color = 'синий'
        case 'PEACH':
            color = 'оранжевый'
        case 'ECRU YELLOW':
            color = 'желтый'
        case 'PALE LILAC':
            color = 'светло-розовый'
        case 'BLUE SHADES':
            color = 'синий'
        case 'DARK YARN':
            color = 'коричневый'
        case 'BLACK-BROWN':
            color = 'коричневый'
        case 'FADED SKY BLUE':
            color = 'голубой'
        case 'MEDIUM KHAKI':
            color = 'хаки'
        case 'APPLE GREEN':
            color = 'зеленый'
        case 'NUDE':
            color = 'прозрачный'
        case 'ANTHRACITE KHAKI':
            color = 'хаки'
        case 'PALE ECRU':
            color = 'бежевый'
        case 'LAVENDER':
            color = 'фиолетовый'
        case 'INDIGO BLUE':
            color = 'синий'
        case 'GREENISH BLUE':
            color = 'зеленый'
        case 'RED NAVY':
            color = 'красный'
        case 'BEIGE BROWN':
            color = 'коричневый'
        case 'BLUISH NAVY':
            color = 'голубой'
        case 'SPECKLED MAUVE':
            color = 'серый'
        case 'NATURAL GREY':
            color = 'серый'
        case 'MEDIUM MARL':
            color = 'серый'
        case 'YARN':
            color = 'светло-серый'
        case 'DEEP GREEN':
            color = 'зеленый'
        case 'DARK OCHRE':
            color = 'коричневый'
        case 'DARK MULBERRY':
            color = 'синий'
        case 'DARK MARL':
            color = 'светло-серый'
        case 'LEATHER':
            color = 'коричневый'
        case 'GREY BLUE':
            color = 'зеленый'
        case 'NEON BLUE':
            color = 'синий'
        case 'RASPBERRY':
            color = 'розовый'
        case 'PALE STONE GREY':
            color = 'серый'
        case 'LAVENDER BLUE':
            color = 'синий'
        case 'PALE GREEN':
            color = 'зеленый'
        case 'BROWN-T':
            color = 'коричневый'
        case 'STRAWBERRY':
            color = 'розовый'
        case 'BLUISH TONE':
            color = 'голубой'
        case 'PALE PURPLE':
            color = 'фиолетовый'
        case 'VARIOUS':
            color = 'коричневый'
        case 'LAGOON GREEN':
            color = 'зеленый'
        case 'PEARL MARL':
            color = 'серый'
        case 'PETROLEUM':
            color = 'серый'
        case 'PASTEL GREEN':
            color = 'зеленый'
        case 'PALE BROWN':
            color = 'коричневый'
        case 'CLAY':
            color = 'коричневый'
        case 'ROSE PINK':
            color = 'розовый'
        case 'GREEN / GREY':
            color = 'серый'
        case 'ECRU/WHITE':
            color = 'белый'
        case 'ECRU/KHAKI':
            color = 'хаки'
        case 'DARK MAROON':
            color = 'коричневый'
        case 'LILAC PINK':
            color = 'розовый'
        case 'WHITE/BLACK':
            color = 'белый'
        case 'ECRU/NAVY':
            color = 'черный'
        case 'WHITE/GREY':
            color = 'белый'
        case 'SAND/KHAKI':
            color = 'хаки'
        case 'BLUE/WHITE':
            color = 'белый'
        case 'SAND/BLUE':
            color = 'голубой'
        case 'WHITE/RED':
            color = 'белый'
        case 'ECRU/YELLOW':
            color = 'желтый'
        case 'BEIGE / GREEN':
            color = 'зеленый'
        case 'BROWN/WHITE':
            color = 'коричневый'
        case 'GREY/BLUE':
            color = 'серый'
        case 'ECRU/GREEN':
            color = 'зеленый'
        case 'GREEN/ECRU':
            color = 'зеленый'
        case 'ECRU/BLACK':
            color = 'черный'
        case 'ECRU/BLUE':
            color = 'горлубой'
        case 'BEIGE/BROWN':
            color = 'коричневый'
        case 'ECRU/BEIGE':
            color = 'бежевый'
        case 'RED/NAVY':
            color = 'красный'
        case 'WHITE/NAVY':
            color = 'белый'
        case 'NAVY/WHITE':
            color = 'белый'
        case 'BROWN/ORANGE':
            color = 'коричневый'
        case 'BLACK/ECRU':
            color = 'черный'
        case 'WATER GREEN':
            color = 'зеленый'
        case 'PALE BURGUNDY':
            color = 'бордовый'
        case 'ANTHRACITE/KHAKI':
            color = 'хаки'
        case 'MEDIUM CAMEL':
            color = 'бежевый'
        case 'MULBERRY':
            color = 'серый'
        case _:
            color = value

    return color


# Функция для перевода формата цветов Pull and Bear в Ozone
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
def sizes_format(format: str, gender: str, size_eur: str) -> str:
    sizes_dict = {
        'alpha': {
            'WOMEN': {
                'XXS': '38',
                'XS-S': '40;44',
                'XS': '42',
                'S': '44',
                'S-M': '44;50',
                'M': '44;46',
                'M-L': '46;50',
                'L': '48;50',
                'L-XL': '48;52',
                'XL': '50;52',
                'XL-XXL': '50;54',
                'XXL': '54'
            },
            'MEN': {
                'XS': '44',
                'S': '46',
                'S-M': '46;48',
                'M': '48',
                'L': '50;52',
                'L-XL': '50;54',
                'XL': '52;54',
                'XXl': '56'
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
                '48': '54',
                '50': '56'
            },
            'MEN': {
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

        # Определяем язык текста
        detected = translator.detect(text)

        if detected.lang == 'en':
            # Переводим текст на русский, если он на английском
            translation = translator.translate(text, dest='ru')
            return translation.text
        else:
            # Оставляем текст без изменений, если он не на английском
            return text
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
