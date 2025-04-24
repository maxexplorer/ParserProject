# bot.py

import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from configs.config import token
from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats

bot = Bot(token=token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

active_parsers = {}


def process_chat_url(chat_url):
    """Вспомогательная функция для обработки URL чатов"""
    return chat_url.strip().replace("https://t.me/", "").lstrip("@")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    chat_id = str(message.chat.id)
    print(chat_id)
    await message.answer("Привет! Я бот для мониторинга сообщений.")

    user_data = load_user_data(chat_id)
    parser = TelegramKeywordParser(
        keywords=user_data.get("keywords", []),
        chats=user_data.get("chats", []),
        bot=bot,
        chat_id=chat_id
    )
    # active_parsers[chat_id] = asyncio.create_task(parser.run())
    active_parsers[chat_id] = parser
    asyncio.create_task(parser.run())  # запускаем отдельно



@dp.message_handler(lambda msg: msg.text.startswith("+") and not msg.text.startswith("+чат"))
async def add_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=True)

    # Обновляем парсер с новыми ключевыми словами
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Добавлены ключевые слова: {', '.join(keywords)}")


@dp.message_handler(lambda msg: msg.text.startswith("-") and not msg.text.startswith("-чат"))
async def remove_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=False)

    # Обновляем парсер с новыми ключевыми словами
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Удалены ключевые слова: {', '.join(keywords)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("+чат"))
async def add_chats(message: types.Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[4:].split()]
    update_chats(chat_id, chats)

    # Обновляем парсер с новыми чатами
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Добавлены чаты: {', '.join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("-чат"))
async def remove_chats(message: types.Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[5:].split()]

    # Удаляем чаты
    update_chats(chat_id, chats, add=False)

    # Обновляем парсер с новыми чатами
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Удалены чаты: {', '.join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("показать слова"))
async def show_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    keywords = user_data.get("keywords", [])
    if keywords:
        await message.answer(f"Ключевые слова:\n{chr(10).join(keywords)}")
    else:
        await message.answer("У вас нет добавленных ключевых слов.")


@dp.message_handler(lambda msg: msg.text.lower().startswith("показать чаты"))
async def show_chats(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    chats = user_data.get("chats", [])
    if chats:
        await message.answer(f"Чаты:\n{chr(10).join(chats)}")
    else:
        await message.answer("У вас нет добавленных чатов.")


def start_bot():
    executor.start_polling(dp)
