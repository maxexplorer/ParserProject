import requests

from googletrans import Translator

# Функция для перевода формата цветов
def colors_format_en(value: str) -> str:
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
        color = 'белый'
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


# Функция для перевода формата цветов
def colors_format_ru(value: str) -> str:
    if value == 'АНТРАЦИТОВО-СЕРЫЙ':
        color = 'серый'
    elif value == 'ЖЕЛТОВАТО-БЕЛЫЙ':
        color = 'белый'
    elif value == 'ЧЕРНЫЙ':
        color = 'черный'
    elif value == 'КРАСНЫЙ':
        color = 'красный'
    elif value == 'ЯРКИЙ КРАСНЫЙ':
        color = 'красный'
    elif value == 'ЭКРЮ':
        color = 'бежевый'
    elif value == 'ИЗУМРУДНЫЙ':
        color = 'изумрудный'
    elif value == 'РАЗНОЦВЕТНЫЙ':
        color = 'разноцветный'
    elif value == 'СВЕТЛО-БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'РЫЖЕВАТО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ЦВЕТ СОСТАРЕННОГО ЗОЛОТА':
        color = 'золотой'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/ БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'ХАКИ':
        color = 'хаки'
    elif value == 'МОРСКОЙ СИНИЙ':
        color = 'синий'
    elif value == 'ГОЛУБОЙ':
        color = 'голубой'
    elif value == 'ЯРКО-РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'СИНИЙ / ИНДИГО':
        color = 'синий'
    elif value == 'СЕРЕБРИСТЫЙ':
        color = 'серебристый'
    elif value == 'РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'СЕРЫЙ':
        color = 'серый'
    elif value == 'ЯРКО-СИНИЙ':
        color = 'синий'
    elif value == 'ЦВЕТ ФУКСИИ':
        color = 'фиолетовый'
    elif value == 'БЕЛЫЙ':
        color = 'белый'
    elif value == 'СИНИЙ':
        color = 'синий'
    elif value == 'ПЕСОЧНЫЙ':
        color = 'песочный'
    elif value == 'ТЕМНЫЙ ХАКИ':
        color = 'хаки'
    elif value == 'Синий/Белый':
        color = 'синий'
    elif value == 'СВЕТЛО-СЕРЫЙ':
        color = 'серый'
    elif value == 'СЕРЫЙ / СИНИЙ':
        color = 'синий'
    elif value == 'ЧЕРНЫЙ / БЕЛЫЙ':
        color = 'черный'
    elif value == 'МЯГКИЙ КАШТАНОВЫЙ':
        color = 'коричневый'
    elif value == 'ТРАВЯНОЙ':
        color = 'зеленый'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/ТЕМНО-СИНИЙ':
        color = 'синий'
    elif value == 'ИНДИГО':
        color = 'синий'
    elif value == 'ТЕЛЕСНО-РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'ЗОЛОТИСТЫЙ':
        color = 'золотой'
    elif value == 'nan':
        color = 'белый'
    elif value == 'ЭКРЮ / ЧЕРНЫЙ':
        color = 'черный'
    elif value == 'СЕРЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'серый'
    elif value == 'МАРЕНГО С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'серый'
    elif value == 'НАТУРАЛЬНЫЙ СЕРЫЙ':
        color = 'серый'
    elif value == 'СВЕТЛЫЙ ХАКИ':
        color = 'хаки'
    elif value == 'ВЫЦВЕТШИЙ СИНИЙ':
        color = 'синий'
    elif value == 'LIME FIZZ':
        color = 'желтый'
    elif value == 'КРЕМОВЫЙ':
        color = 'кремовый'
    elif value == 'МЯГКИЙ СЕРЫЙ':
        color = 'серый'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'КАМЕННО-СЕРЫЙ':
        color = 'серый'
    elif value == 'УГОЛЬНЫЙ':
        color = 'черный'
    elif value == 'СВЕТЛЫЙ ЖЕЛТО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ЗЕЛЕНОВАТЫЙ':
        color = 'зеленый'
    elif value == 'ПАСТЕЛЬНО-РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'СЕРО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'НЕБЕСНО-ГОЛУБОЙ':
        color = 'голубой'
    elif value == 'ЦВЕТ МХА':
        color = 'зеленый'
    elif value == 'ЕДИНСТВЕННЫЙ':
        color = 'белый'
    elif value == 'СВЕТЛЫЙ РЫЖЕВАТО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ТЕМНО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ПУДРОВО-РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'СЕРОВАТО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'НЕФТЯНОЙ':
        color = 'черный'
    elif value == 'ТЕМНО-СЕРЫЙ':
        color = 'серый'
    elif value == 'ЦВЕТ ЛЬДА':
        color = 'прозрачный'
    elif value == 'СВЕТЛО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ТЕМНЫЙ ИНДИГО':
        color = 'синий'
    elif value == 'СЕРО-СИНИЙ':
        color = 'синий'
    elif value == 'ЦВЕТ РОЗОВОГО ДЕРЕВА':
        color = 'розовый'
    elif value == 'ЧЕРНЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'черный'
    elif value == 'ЛЕОПАРДОВЫЙ':
        color = 'леопардовый'
    elif value == 'ЛИЛОВЫЙ':
        color = 'лиловый'
    elif value == 'МАДЖЕНТА':
        color = 'лиловый'
    elif value == 'ЗЕЛЕНЫЙ / ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА':
        color = 'зеленый'
    elif value == 'ЦВЕТ ВЫБЕЛЕННОГО ЛЬНА':
        color = 'бежевый'
    elif value == 'ЛАВАНДОВО-СИНИЙ':
        color = 'синий'
    elif value == 'ОРАНЖЕВЫЙ':
        color = 'оранжевый'
    elif value == 'БЕЛЫЙ / КРАСНЫЙ':
        color = 'красный'
    elif value == 'С ПРИНТОМ':
        color = 'разноцветный'
    elif value == 'ТЕМНО-СИНИЙ/БЕЛЫЙ':
        color = 'синий'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/ ХАКИ':
        color = 'хаки'
    elif value == 'ТЕРРАКОТОВЫЙ':
        color = 'терракотовый'
    elif value == 'СИНИЙ ЭЛЕКТРИК':
        color = 'синий'
    elif value == 'ЛИМОННЫЙ':
        color = 'желтый'
    elif value == 'ТЕМНЫЙ БЕЖЕВО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'ОТТЕНКИ СИНЕГО':
        color = 'синий'
    elif value == 'ЦВЕТ ОЛИВКОВОГО МАСЛА':
        color = 'оливковый'
    elif value == 'ТЕМНО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'МАЛИНОВЫЙ':
        color = 'малиновый'
    elif value == 'СВЕТЛЫЙ СЕРО-КОРИЧНЕВЫЙ':
        color = 'серый'
    elif value == 'ВОДЯНИСТЫЙ ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'ЗЕЛЕНЫЙ/БЕЛЫЙ':
        color = 'зеленый'
    elif value == 'РОЗОВЫЙ / БЕЛЫЙ':
        color = 'розовый'
    elif value == 'ГОРЧИЧНЫЙ':
        color = 'горчичный'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/СИНИЙ':
        color = 'синий'
    elif value == 'МАНДАРИНОВЫЙ':
        color = 'оранжевый'
    elif value == 'ОЛИВКОВЫЙ':
        color = 'оливковый'
    elif value == 'ЯБЛОЧНО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'СВЕТЛАЯ ФУКСИЯ':
        color = 'малиновый'
    elif value == 'КАВА':
        color = 'зеленый'
    elif value == 'ОТТЕНОК КОРИЧНЕВОГО':
        color = 'коричневый'
    elif value == 'ОТТЕНКИ ЗЕЛЕНОГО':
        color = 'зеленый'
    elif value == 'ПЕРСИКОВЫЙ':
        color = 'персиковый'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/КРАСНЫЙ':
        color = 'красный'
    elif value == 'НАСЫЩЕННЫЙ КРАСНЫЙ':
        color = 'красный'
    elif value == 'бежевый ':
        color = 'оранжевый'
    elif value == 'НЕОНОВО-ЛАЙМОВЫЙ':
        color = 'зеленый'
    elif value == 'СИРЕНЕВЫЙ':
        color = 'сиреневый'
    elif value == 'ЦВЕТ РОЗОВОГО МЕЛА':
        color = 'розовый'
    elif value == 'ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'КОРИЧНЕВЫЙ/БЕЛЫЙ':
        color = 'коричневый'
    elif value == 'БЕЛЫЙ / ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'B':
        color = 'белый'
    elif value == 'ПАСТЕЛЬНО-ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'СВИНЦОВЫЙ':
        color = 'серый'
    elif value == 'ЧЕРНЫЙ / ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА':
        color = 'черный'
    elif value == 'СЕРЫЙ / БЕЖЕВЫЙ':
        color = 'черный'
    elif value == 'ЧЕРНЫЙ / ЗЕЛЕНЫЙ':
        color = 'черный'
    elif value == 'СВЕТЛО-КРАСНЫЙ':
        color = 'красный'
    elif value == 'НЕОНОВО-СИНИЙ':
        color = 'синий'
    elif value == 'ЛАЙМОВЫЙ':
        color = 'зеленый'
    elif value == 'ОТТЕНКИ РОЗОВОГО':
        color = 'розовый'
    elif value == 'КОРАЛЛОВЫЙ':
        color = 'коралловый'
    elif value == 'ЦВЕТ СЛИВОЧНОГО МАСЛА':
        color = 'желтый'
    elif value == 'ПОЛОСКИ':
        color = 'разноцветный'
    elif value == 'ЧЕРНЫЙ / СЕРЕБРЯНЫЙ':
        color = 'серебристый'
    elif value == 'СВЕТЛО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'СВЕТЛО-ОЛИВКОВЫЙ':
        color = 'оливковый'
    elif value == 'ПАСТЕЛЬНО-СИНИЙ':
        color = 'синий'
    elif value == 'КОРИЧНЕВО-СИНИЙ':
        color = 'синий'
    elif value == 'РОЗОВЫЙ / ЛИЛОВЫЙ':
        color = 'лиловый'
    elif value == 'БЕЖЕВЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'бежевый'
    elif value == 'ЧЕРНИЛЬНО-СИНИЙ':
        color = 'синий'
    elif value == 'ШОКОЛАДНЫЙ':
        color = 'шоколадный'
    elif value == 'ПЫЛЬНЫЙ ХАКИ':
        color = 'хаки'
    elif value == 'ПАСТЕЛЬНО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'БЕЛЫЙ / ЧЕРНЫЙ':
        color = 'черный'
    elif value == 'ЗОЛОТОЙ':
        color = 'золотой'
    elif value == 'ВИННЫЙ':
        color = 'бордовый'
    elif value == 'ПЕСОЧНЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'песочный'
    elif value == 'ЧЕРНЫЙ / ЗОЛОТОЙ':
        color = 'золотой'
    elif value == 'БУТЫЛОЧНО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'ТЕМНЫЙ АНТРАЦИТ':
        color = 'серый'
    elif value == 'ЖЕМЧУЖНО-СЕРЫЙ':
        color = 'серый'
    elif value == 'КРАСНЫЙ / БЕЛЫЙ':
        color = 'красный'
    elif value == 'БЕЛЫЙ / СЕРЫЙ':
        color = 'серый'
    elif value == 'ЛИМОННО-ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'СЕРО-ДЫМЧАТЫЙ':
        color = 'белый'
    elif value == 'МЯГКИЙ РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'БЕЛЫЙ / РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'ЦВЕТ ЗЕЛЕНОЙ ТРАВЫ':
        color = 'зеленый'
    elif value == 'СВЕТЛО-ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'Песочный/Коричневый':
        color = 'коричневый'
    elif value == 'ПАСТЕЛЬНАЯ МАЛЬВА':
        color = 'бордовый'
    elif value == 'ОХРА':
        color = 'оранжевый'
    elif value == 'ЦВЕТ МАЛЬВЫ':
        color = 'бордовый'
    elif value == 'ЗЕЛЕНОВАТО-СИНИЙ':
        color = 'зеленый'
    elif value == 'МЯГКИЙ ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'ЗЕБРА':
        color = 'разноцветный'
    elif value == 'ЛИНЯЛЫЙ НЕФТЯНОЙ':
        color = 'черный'
    elif value == 'СЕРОВАТЫЙ':
        color = 'серый'
    elif value == 'КРАСНО-ОРАНЖЕВЫЙ':
        color = 'красный'
    elif value == 'КОРИЧНЕВЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'коричневый'
    elif value == 'ЗЕЛЕНЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'зеленый'
    elif value == 'СВЕТЛЫЙ ЭКРЮ':
        color = 'бежевый'
    elif value == 'МОРСКОЙ ЯРКО-СИНИЙ':
        color = 'синий'
    elif value == 'ВАНИЛЬНЫЙ':
        color = 'бежевый'
    elif value == 'ЦВЕТ МОРСКОЙ ВОЛНЫ':
        color = 'голубой'
    elif value == 'ФИСТАШКОВЫЙ':
        color = 'фисташковый'
    elif value == 'СВЕТЛО-РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'КОРИЧНЕВЫЙ / ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА':
        color = 'коричневый'
    elif value == 'СВЕТЛО-СИРЕНЕВЫЙ':
        color = 'сиреневый'
    elif value == 'Красный / Черный':
        color = 'красный'
    elif value == 'Неоновый розовый':
        color = 'розовый'
    elif value == 'Коричневый / Белый':
        color = 'коричневый'
    elif value == 'ШОКОЛАДНО-КОРИЧНЕВЫЙ':
        color = 'шоколадный'
    elif value == 'СТАЛЬНОЙ СИНИЙ':
        color = 'синий'
    elif value == 'РЫЖЕВАТО-КОРИЧНЕВЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'коричневый'
    elif value == 'СВЕТЛО-ФИСТАШКОВЫЙ':
        color = 'фисташковый'
    elif value == 'МЕДНЫЙ':
        color = 'медный'
    elif value == 'ТЕМНО-БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'МАРСАЛА':
        color = 'ПЕРСИКОВЫЙ'
    elif value == 'ЯГОДНЫЙ':
        color = 'бордовый'
    elif value == 'БЕЛЫЙ/БИРЮЗОВЫЙ':
        color = 'белый'
    elif value == 'ЦВЕТ БУРГУНДСКОГО ВИНА':
        color = 'бордовый'
    elif value == 'МЯГКИЙ ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'СИНИЙ / ЧЕРНЫЙ':
        color = 'черный'
    elif value == 'КОБАЛЬТОВЫЙ':
        color = 'серый'
    elif value == 'БЕЛЫЙ / МОРСКОЙ СИНИЙ':
        color = 'белый'
    elif value == 'ОТТЕНОК ЗЕЛЕНОГО':
        color = 'зеленый'
    elif value == 'Лиловый / Белый':
        color = 'белый'
    elif value == 'ВАСИЛЬКОВЫЙ':
        color = 'фиолетовый'
    elif value == 'СВЕТЛО-ГОЛУБОЙ':
        color = 'голубой'
    elif value == 'ЦВЕТ НЕБЕЛЕНОГО ПОЛОТНА/ГРАНАТОВЫЙ':
        color = 'гранатовый'
    elif value == 'КОРАЛЛОВО-КРАСНЫЙ':
        color = 'красный'
    elif value == 'ВОДЯНИСТО-ГОЛУБОЙ':
        color = 'голубой'
    elif value == 'ГЛУБОКИЙ СИНИЙ':
        color = 'синий'
    elif value == 'КОСТЯНОЙ':
        color = 'белый'
    elif value == 'ЦВЕТ НОЧНОГО НЕБА':
        color = 'синий'
    elif value == 'СЛОНОВАЯ КОСТЬ':
        color = 'белый'
    elif value == 'СЕРО-КОРИЧНЕВЫЙ С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'коричневый'
    elif value == 'ЛИНЯЛЫЙ СИНИЙ':
        color = 'синий'
    elif value == 'ОТТЕНОК ЧЕРНОГО':
        color = 'черный'
    elif value == 'СВЕТЛО-ПЕСОЧНЫЙ':
        color = 'песочный'
    elif value == 'МОРСКОЙ ТЕМНО-СИНИЙ':
        color = 'синий'
    elif value == 'ЭКРЮ / С МЕЛАНЖЕВЫМ ЭФФЕКТОМ':
        color = 'бежевый'
    elif value == 'ЛИНЯЛЫЙ ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'ЦВЕТ СЛОНОВОЙ КОСТИ':
        color = 'белый'
    elif value == 'БИЛЬЯРДНЫЙ ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'ОТТЕНКИ ФИОЛЕТОВОГО':
        color = 'фиолетовый'
    elif value == 'ТАБАЧНЫЙ':
        color = 'табачный'
    elif value == 'ТЕМНО-ОРАНЖЕВЫЙ':
        color = 'оранжевый'
    elif value == 'УТИНО-СИНИЙ':
        color = 'синий'
    elif value == 'ЗЕЛЕНЫЙ / СЕРЫЙ':
        color = 'зеленый'
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

