import re

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from configs.config import token


bot = Bot(token=token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Хэндлер на команду /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Привет! Я бот для мониторинга сообщений.")

# Хэндлер на добавление ключевых слов с помощью символа "+"
@dp.message_handler(lambda message: message.text.startswith('+'))
async def add_keywords(message: types.Message):
    keywords = [kw.strip() for kw in re.split('[, \n]+', message.text[1:]) if kw.strip()]
    if keywords:
        with open("keywords.txt", "a", encoding="utf-8") as f:
            for keyword in keywords:
                f.write(keyword + "\n")
        await message.reply(f"Ключевые слова {', '.join(keywords)} добавлены.")
    else:
        await message.reply("Пожалуйста, укажите ключевые слова после символа +.")

# Хэндлер на удаление ключевых слов с помощью символа "-"
@dp.message_handler(lambda message: message.text.startswith('-'))
async def remove_keywords(message: types.Message):
    keywords = [kw.strip() for kw in re.split('[, \n]+', message.text[1:]) if kw.strip()]
    if keywords:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            existing_keywords = f.readlines()

        with open("keywords.txt", "w", encoding="utf-8") as f:
            for line in existing_keywords:
                if line.strip("\n") not in keywords:
                    f.write(line)

        await message.reply(f"Ключевые слова {', '.join(keywords)} удалены.")
    else:
        await message.reply("Пожалуйста, укажите ключевые слова после символа -.")

# Хэндлер на добавление чатов
@dp.message_handler(lambda message: message.text.startswith("Добавить чаты"))
async def add_chats(message: types.Message):
    chats = [chat.strip() for chat in re.split('[, \n]+', message.text.split(" ", 1)[1]) if chat.strip()]
    if chats:
        with open("chats.txt", "a", encoding="utf-8") as f:
            for chat in chats:
                f.write(chat + "\n")
        await message.reply(f"Чаты {', '.join(chats)} добавлены.")
    else:
        await message.reply("Пожалуйста, укажите чаты для добавления.")

# Запуск бота
async def start_bot():
    print("Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
