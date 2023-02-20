import json

from aiogram import Bot, Dispatcher, executor, types
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start', 'welcome', 'about'])
async def start(message: types.Message):
    await message.answer('What is up Doc?')


@dp.message_handler(commands='all_news')
async def get_all_news(message: types.Message):
    with open('data/news_dict.json', 'r', encoding='utf-8') as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
        news = f"{v['article_date_time']}\n" \
               f"{v['article_title']}\n" \
               f"{v['article_desc']}\n" \
               f"{v['article_url']}"
        await message.answer(news)



if __name__ == '__main__':
    executor.start_polling(dp)
