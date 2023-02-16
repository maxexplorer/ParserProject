from aiogram import Bot, Dispatcher, executor, types
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot=bot)

dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.reply('What is up Doc?')

if __name__ == '__main__':
    executor.start_polling(dp)



