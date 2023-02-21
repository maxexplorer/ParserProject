import json

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from config import token
from main import get_first_news, check_news_update

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Все новости', 'Свежие новости']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Лента новостей', reply_markup=keyboard)


@dp.message_handler(Text(equals='Все новости'))
async def get_all_news(message: types.Message):
    with open('data/news_dict.json', 'r', encoding='utf-8') as file:
        news_dict = json.load(file)

    # news_dict = get_first_news()

    for k, v in sorted(news_dict.items()):
        news = f"{hbold(v['article_date_time'])}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals='Свежие новости'))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()

    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(v['article_date_time'])}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)
    else:
        await message.answer('Пока нет свежих новостей...')


if __name__ == '__main__':
    executor.start_polling(dp)
