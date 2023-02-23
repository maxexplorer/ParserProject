import json

from aiogram import Bot, Dispatcher, executor, types
from config import token
from main import headers, get_data

bot = Bot(token=token)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):

    # get_data(headers)

    with open('data/result_list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for i in data:
        items = f"{i['title']}"
        await message.answer(items)


@dp.message_handler()
async def messages(message: types.Message):
    brand = message.text.lower()
    await message.answer(brand)

dp.message_handler(content_types=["text"])
async def text_chat(message):
    a = message.get_current()["text"]



if __name__ == '__main__':
    executor.start_polling(dp)
