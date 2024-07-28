import requests

from googletrans import Translator

# Функция для перевода формата цветов Massimo Dutti в Ozone
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
        color = value.lower()

    return color

# Функция для перевода европейских размеров в российские
def sizes_format(format: str, gender: str, size_eur: str) -> str:
    sizes_dict = {
        'alpha': {
            'женский': {
                'XXS': '40',
                'XS': '42',
                'XS-S': '42;44',
                'S': '44',
                'M': '46;48',
                'L': '48;50',
                'M-L': '46;50',
                'XL': '50;52'
            },
            'мужской': {
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
            'женский': {
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
            'мужской': {
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

