import re
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from configs.config import token
from parser import TelegramKeywordParser  # Предположим, что у нас есть класс парсера в parser.py

bot = Bot(token=token)
dp = Dispatcher(bot)


# Хэндлер на команду /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # Получаем chat_id пользователя (чата с ботом)
    chat_id = message.chat.id

    await message.reply("Привет! Я бот для мониторинга сообщений.")

    # Загружаем чаты и ключевые слова из файлов
    try:
        with open('data/chats.txt', 'r', encoding='utf-8') as file:
            chats = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        chats = []

    try:
        with open('data/keywords.txt', 'r', encoding='utf-8') as file:
            keywords = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        keywords = []

    # Создаем экземпляр парсера и передаем chat_id
    parser = TelegramKeywordParser(keywords, chats, bot, chat_id)

    # Запускаем парсер в фоновом режиме (через asyncio)
    await parser.run()


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
if __name__ == '__main__':
    executor.start_polling(dp)
