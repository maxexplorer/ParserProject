import requests

from googletrans import Translator


# Функция для перевода формата цветов
def colors_format_en(value: str) -> str:
    if value == 'White':
        color = 'белый'
    elif value == 'Khaki':
        color = 'хаки'
    elif value == 'Black':
        color = 'черный'
    elif value == 'Brown_taupe':
        color = 'серый'
    elif value == 'Navy blue':
        color = 'темно-синий'
    elif value == 'Blue':
        color = 'голубой'
    elif value == 'Bright red':
        color = 'красный'
    elif value == 'Blue_white':
        color = 'синий'
    elif value == 'Pearl grey':
        color = 'светло-серый'
    elif value == 'Anthracite grey':
        color = 'светло-серый'
    elif value == 'Ecru':
        color = 'бежевый'
    elif value == 'Fuchsia':
        color = 'перламутровый'
    elif value == 'Grey marl':
        color = 'серый'
    elif value == 'Blue':
        color = 'синий'
    elif value == 'Stone':
        color = 'серый'
    elif value == 'Mid-grey':
        color = 'серый'
    elif value == 'Ecru':
        color = 'светло-бежевый'
    elif value == 'Grey':
        color = 'серый'
    elif value == 'Light brown':
        color = 'коричневый'
    elif value == 'Light khaki':
        color = 'хаки'
    elif value == 'Sand':
        color = 'коричневый'
    elif value == 'Light blue':
        color = 'синий'
    elif value == 'Blue grey':
        color = 'серый'
    elif value == 'Ice':
        color = 'светло-синий'
    elif value == 'Black_silver':
        color = 'серебристый'
    elif value == 'Light beige':
        color = 'светло-бежевый'
    elif value == 'Beige-pink':
        color = 'розовый'
    elif value == 'camel':
        color = 'желтый'
    elif value == 'Camel':
        color = 'светло-бежевый'
    elif value == 'Mid-blue':
        color = 'светло-синий'
    elif value == 'Grey_beige':
        color = 'серый'
    elif value == 'Darkred':
        color = 'красный'
    elif value == 'Red':
        color = 'красный'
    elif value == 'Sand':
        color = 'светло-бежевый'
    elif value == 'Multicoloured':
        color = 'разноцветный'
    elif value == 'Ecru_black':
        color = 'черный'
    elif value == 'Chocolate':
        color = 'коричневый'
    elif value == 'Beige':
        color = 'светло-бежевый'
    elif value == 'Camel_white':
        color = 'белый'
    elif value == 'Ecru_blue':
        color = 'голубой'
    elif value == 'Blues':
        color = 'синий'
    elif value == 'Beige marl':
        color = 'бежевый'
    elif value == 'Light ecru':
        color = 'светло-бежевый'
    elif value == 'Blue_navy':
        color = 'синий'
    elif value == 'Dark anthracite':
        color = 'светло-серый'
    elif value == 'Dark brown':
        color = 'коричневый'
    elif value == 'Silver':
        color = 'серебристый'
    elif value == 'Greenish':
        color = 'зеленый'
    elif value == 'Mid khaki':
        color = 'хаки'
    elif value == 'Skyblue':
        color = 'голубой'
    elif value == 'Moss green':
        color = 'зеленый'
    elif value == 'Darkkhaki':
        color = 'хаки'
    elif value == 'Bronze':
        color = 'светло-коричневый'
    elif value == 'Mink':
        color = 'белый'
    elif value == 'Green':
        color = 'зеленый'
    elif value == 'Dark camel':
        color = 'желтый'
    elif value == 'Darkgrey':
        color = 'серый'
    elif value == 'Bluish':
        color = 'серый'
    elif value == 'Lilac_white':
        color = 'белый'
    elif value == 'Tan marl':
        color = 'белый'
    elif value == 'Sand_brown':
        color = 'коричневый'
    elif value == 'Charcoal grey':
        color = 'серый'
    elif value == 'Tobacco':
        color = 'коричневый'
    elif value == 'Black_ecru':
        color = 'бежевый'
    elif value == 'Wine':
        color = 'бордовый'
    elif value == 'Light camel':
        color = 'желтый'
    elif value == 'Black gold':
        color = 'золотой'
    elif value == 'Brown':
        color = 'коричневый'
    elif value == 'Ecru_maroon':
        color = 'бежевый'
    elif value == 'Darkgreen':
        color = 'зеленый'
    elif value == 'Cream':
        color = 'бежевый'
    elif value == 'Mink':
        color = 'бежевый'
    elif value == 'Lightgrey':
        color = 'светло-серый'
    elif value == 'Striped':
        color = 'белый'
    elif value == 'Cava':
        color = 'белый'
    elif value == 'Taupe grey':
        color = 'серый'
    elif value == 'Beige':
        color = 'бежевый'
    elif value == 'Navy_white':
        color = 'белый'
    elif value == 'Black_green':
        color = 'зеленый'
    elif value == 'Golden':
        color = 'золотой'
    elif value == 'Petrol blue':
        color = 'голубой'
    elif value == 'Olive green':
        color = 'оливковый'
    elif value == 'Ink blue':
        color = 'синий'
    elif value == 'Pink_lilac':
        color = 'розовый'
    elif value == 'Emerald':
        color = 'зеленый'
    elif value == 'Dark beige':
        color = 'бежевый'
    elif value == 'Dark grey marl':
        color = 'серый'
    elif value == 'Black_white':
        color = 'белый'
    elif value == 'Chocolate brown':
        color = 'коричневый'
    elif value == 'Blue_indigo':
        color = 'синий'
    elif value == 'Charcoal':
        color = 'серый'
    elif value == 'Blue_grey':
        color = 'серый'
    elif value == 'Indigo':
        color = 'синий'
    elif value == 'Washed petrol':
        color = 'белый'
    elif value == 'Sand_marl':
        color = 'бежевый'
    elif value == 'Gold':
        color = 'золотой'
    elif value == 'Indigo':
        color = 'светло-синий'
    elif value == 'Bottle green':
        color = 'разноцветный'
    elif value == 'Charcoal':
        color = 'белый'
    elif value == 'Grey_natural':
        color = 'серый'
    elif value == 'Stripes':
        color = 'белый'
    elif value == 'Lightgreen':
        color = 'светло-зеленый'
    elif value == 'Dirty-mauve':
        color = 'разноцветный'
    elif value == 'Ecru_beige':
        color = 'бежевый'
    elif value == 'Midnigh tblue':
        color = 'голубой'
    elif value == 'Bluish':
        color = 'синий'
    elif value == 'Apple green':
        color = 'зеленый'
    elif value == 'Pink_white':
        color = 'pink_white'
    elif value == 'Red/white':
        color = 'red/white'
    elif value == 'Светло-бежевый':
        color = 'светло-бежевый'
    elif value == 'Pink':
        color = 'розовый'
    elif value == 'Mid-camel':
        color = 'желтый'
    elif value == 'Mid-pink':
        color = 'розовый'
    elif value == 'Intense red':
        color = 'красный'
    elif value == 'Grey_blue':
        color = 'серый'
    elif value == 'Light yellow':
        color = 'желтый'
    elif value == 'Mid-mink':
        color = 'mid-mink'
    elif value == 'Bone':
        color = 'белый'
    elif value == 'Brick':
        color = 'белый'
    elif value == 'Mid-green':
        color = 'зеленый'
    elif value == 'Dusty pink':
        color = 'розовый'
    elif value == 'Green_ecru':
        color = 'бежевый'
    elif value == 'Maroon':
        color = 'бордовый'
    elif value == 'Duck green':
        color = 'зеленый'
    elif value == 'Mid-turquoise':
        color = 'голубой'
    elif value == 'Green_blue':
        color = 'голубой'
    elif value == 'Dark mauve':
        color = 'белый'
    elif value == 'Faded pink':
        color = 'розовый'
    elif value == 'Maroon grey':
        color = 'серый'
    elif value == 'Reddish':
        color = 'красный'
    elif value == 'Orange':
        color = 'оранжевый'
    elif value == 'Mid-ecru':
        color = 'бежевый'
    elif value == 'Pale pink':
        color = 'розовый'
    elif value == 'Seagreen':
        color = 'светло-синий'
    elif value == 'Blue_green':
        color = 'зеленый'
    elif value == 'Ecru_marl':
        color = 'бежевый'
    elif value == 'Printed':
        color = 'белый'
    elif value == 'Apricot':
        color = 'оранжевый'
    elif value == 'Mauve':
        color = 'сиреневый'
    elif value == 'Mink marl':
        color = 'белый'
    elif value == 'Terracotta':
        color = 'белый'
    elif value == 'Grey ish':
        color = 'серый'
    elif value == 'Dark navy':
        color = 'синий'
    elif value == 'Ochre':
        color = 'оранжевый'
    elif value == 'Ecru_green':
        color = 'зеленый'
    elif value == 'Ochre':
        color = 'коричневый'
    elif value == 'Only one':
        color = 'розовый'
    elif value == 'Green marl':
        color = 'разноцветный'
    elif value == 'Taupe':
        color = 'белый'
    elif value == 'Pink marl':
        color = 'розовый'
    elif value == 'Light grey marl':
        color = 'разноцветный'
    elif value == 'Strawberry':
        color = 'разноцветный'
    elif value == 'Raspberry':
        color = 'малиновый'
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
    elif value == 'Разноцветный':
        color = 'разноцветный'
    elif value == 'СВЕТЛО-БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'БЕЖЕВЫЙ':
        color = 'бежевый'
    elif value == 'ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'РЫЖЕВАТО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'Цвет состаренного золота':
        color = 'золотой'
    elif value == 'Цвет небеленого полотна/ Бежевый':
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
    elif value == 'Черный / Белый':
        color = 'черный'
    elif value == 'МЯГКИЙ КАШТАНОВЫЙ':
        color = 'коричневый'
    elif value == 'ТРАВЯНОЙ':
        color = 'зеленый'
    elif value == 'Цвет небеленого полотна/Темно-синий':
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
    elif value == 'Цвет небеленого полотна/Зеленый':
        color = 'зеленый'
    elif value == 'КАМЕННО-СЕРЫЙ':
        color = 'серый'
    elif value == 'УГОЛЬНЫЙ':
        color = 'черный'
    elif value == 'Светлый желто-коричневый':
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
    elif value == 'Единственный':
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
    elif value == 'Леопардовый':
        color = 'леопардовый'
    elif value == 'ЛИЛОВЫЙ':
        color = 'лиловый'
    elif value == 'Маджента':
        color = 'лиловый'
    elif value == 'Зеленый / Цвет небеленого полотна':
        color = 'зеленый'
    elif value == 'Цвет выбеленного льна':
        color = 'бежевый'
    elif value == 'ЛАВАНДОВО-СИНИЙ':
        color = 'синий'
    elif value == 'ОРАНЖЕВЫЙ':
        color = 'оранжевый'
    elif value == 'Белый / Красный':
        color = 'красный'
    elif value == 'С принтом':
        color = 'разноцветный'
    elif value == 'Темно-синий/Белый':
        color = 'синий'
    elif value == 'Цвет небеленого полотна/ Хаки':
        color = 'хаки'
    elif value == 'ТЕРРАКОТОВЫЙ':
        color = 'терракотовый'
    elif value == 'СИНИЙ ЭЛЕКТРИК':
        color = 'синий'
    elif value == 'ЛИМОННЫЙ':
        color = 'желтый'
    elif value == 'ТЕМНЫЙ БЕЖЕВО-КОРИЧНЕВЫЙ':
        color = 'коричневый'
    elif value == 'Оттенки Синего':
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
    elif value == 'Зеленый/белый':
        color = 'зеленый'
    elif value == 'Розовый / Белый':
        color = 'розовый'
    elif value == 'ГОРЧИЧНЫЙ':
        color = 'горчичный'
    elif value == 'Цвет небеленого полотна/Синий':
        color = 'синий'
    elif value == 'МАНДАРИНОВЫЙ':
        color = 'оранжевый'
    elif value == 'ОЛИВКОВЫЙ':
        color = 'оливковый'
    elif value == 'ЯБЛОЧНО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'СВЕТЛАЯ ФУКСИЯ':
        color = 'малиновый'
    elif value == 'Кава':
        color = 'зеленый'
    elif value == 'ОТТЕНОК КОРИЧНЕВОГО':
        color = 'коричневый'
    elif value == 'ОТТЕНКИ ЗЕЛЕНОГО':
        color = 'зеленый'
    elif value == 'ПЕРСИКОВЫЙ':
        color = 'персиковый'
    elif value == 'Цвет небеленого полотна/Красный':
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
    elif value == 'Желтый':
        color = 'желтый'
    elif value == 'КОРИЧНЕВЫЙ/БЕЛЫЙ':
        color = 'коричневый'
    elif value == 'Белый / Зеленый':
        color = 'зеленый'
    elif value == 'B':
        color = 'белый'
    elif value == 'ПАСТЕЛЬНО-ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'СВИНЦОВЫЙ':
        color = 'серый'
    elif value == 'Черный / Цвет небеленого полотна':
        color = 'черный'
    elif value == 'СЕРЫЙ / БЕЖЕВЫЙ':
        color = 'черный'
    elif value == 'Черный / Зеленый':
        color = 'черный'
    elif value == 'СВЕТЛО-КРАСНЫЙ':
        color = 'красный'
    elif value == 'НЕОНОВО-СИНИЙ':
        color = 'синий'
    elif value == 'ЛАЙМОВЫЙ':
        color = 'зеленый'
    elif value == 'Оттенки розового':
        color = 'розовый'
    elif value == 'КОРАЛЛОВЫЙ':
        color = 'коралловый'
    elif value == 'ЦВЕТ СЛИВОЧНОГО МАСЛА':
        color = 'желтый'
    elif value == 'Полоски':
        color = 'разноцветный'
    elif value == 'Черный / Серебряный':
        color = 'серебристый'
    elif value == 'СВЕТЛО-ЗЕЛЕНЫЙ':
        color = 'зеленый'
    elif value == 'СВЕТЛО-ОЛИВКОВЫЙ':
        color = 'оливковый'
    elif value == 'ПАСТЕЛЬНО-СИНИЙ':
        color = 'синий'
    elif value == 'Коричнево-синий':
        color = 'синий'
    elif value == 'Розовый / Лиловый':
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
    elif value == 'Красный / Белый':
        color = 'красный'
    elif value == 'Белый / Серый':
        color = 'серый'
    elif value == 'ЛИМОННО-ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'Серо-дымчатый':
        color = 'белый'
    elif value == 'МЯГКИЙ РОЗОВЫЙ':
        color = 'розовый'
    elif value == 'Белый / Розовый':
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
    elif value == 'Зебра':
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
    elif value == 'Коричневый / Цвет небеленого полотна':
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
        color = 'персиковый'
    elif value == 'Ягодный':
        color = 'бордовый'
    elif value == 'белый/бирюзовый':
        color = 'белый'
    elif value == 'ЦВЕТ БУРГУНДСКОГО ВИНА':
        color = 'бордовый'
    elif value == 'МЯГКИЙ ЖЕЛТЫЙ':
        color = 'желтый'
    elif value == 'Синий / Черный':
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
    elif value == 'Цвет небеленого полотна/Гранатовый':
        color = 'гранатовый'
    elif value == 'КОРАЛЛОВО-КРАСНЫЙ':
        color = 'красный'
    elif value == 'ВОДЯНИСТО-ГОЛУБОЙ':
        color = 'голубой'
    elif value == 'ГЛУБОКИЙ СИНИЙ':
        color = 'синий'
    elif value == 'КОСТЯНОЙ':
        color = 'белый'
    elif value == 'Цвет ночного неба':
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
    elif value == 'Оттенки Фиолетового':
        color = 'фиолетовый'
    elif value == 'ТАБАЧНЫЙ':
        color = 'табачный'
    elif value == 'ТЕМНО-ОРАНЖЕВЫЙ':
        color = 'оранжевый'
    elif value == 'утино-синий':
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
            'Женщины': {
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
            'Мужчины': {
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
            'Женщины': {
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


# Функция для разделения списка на части по n элементов
def chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
