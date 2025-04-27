# bot.py

import os

from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest

import asyncio
from aiogram import Bot, Dispatcher, executor, types

from configs.config import token
from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats, update_exceptions

bot = Bot(token=token)
dp = Dispatcher(bot)

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
        exceptions=user_data.get("exceptions", []),
        bot=bot,
        chat_id=chat_id
    )

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

    # Пытаемся подписаться на каждый чат через Telethon
    if chat_id in active_parsers:
        client = active_parsers[chat_id].client
        for chat in chats:
            try:
                await client(JoinChannelRequest(chat))
                await asyncio.sleep(1)  # небольшая задержка, чтобы избежать флуд-лимита
            except Exception as e:
                print(f"[!] Ошибка подписки на {chat}: {e}")

    # Обновляем локальные данные
    update_chats(chat_id, chats)

    # Перезагружаем данные в парсер
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Добавлены и подписаны на чаты:\n{chr(10).join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("-чат"))
async def remove_chats(message: types.Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[5:].split()]

    # Пытаемся отписаться от каждого чата через Telethon
    if chat_id in active_parsers:
        client = active_parsers[chat_id].client
        for chat in chats:
            try:
                await client(LeaveChannelRequest(chat))
                await asyncio.sleep(1)  # чтобы не попасть под лимиты
            except Exception as e:
                print(f"[!] Ошибка отписки от {chat}: {e}")

    # Обновляем локальные данные
    update_chats(chat_id, chats, add=False)

    # Перезагружаем данные в парсер
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Удалены и отписаны от чатов:\n{chr(10).join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower() == "спам")
async def add_exception(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Пожалуйста, ответьте на сообщение, которое хотите пометить как спам.")
        return

    spam_sender_id = get_user_id_from_message(message.reply_to_message)
    if spam_sender_id is None:
        await message.answer("❗ Невозможно определить пользователя (скрытый отправитель).")
        return

    chat_id = str(message.chat.id)
    update_exceptions(chat_id, [spam_sender_id], add=True)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Пользователь с ID {spam_sender_id} добавлен в список исключений.")


@dp.message_handler(lambda msg: msg.text.lower().startswith("слова"))
async def show_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    keywords = user_data.get("keywords", [])
    if keywords:
        await message.answer(f"Ключевые слова:\n{chr(10).join(keywords)}")
    else:
        await message.answer("У вас нет добавленных ключевых слов.")


@dp.message_handler(lambda msg: msg.text.lower().startswith("чаты"))
async def show_chats(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    chats = user_data.get("chats", [])
    if chats:
        await message.answer(f"Чаты:\n{chr(10).join(chats)}")
    else:
        await message.answer("У вас нет добавленных чатов.")


def get_user_id_from_message(message: types.Message) -> int | None:
    """Возвращает ID пользователя из сообщения, если возможно."""
    # if message.forward_from:
    #     return message.forward_from.id  # Переслано и ID доступен
    if message.reply_to_message:
        return message.reply_to_message.from_user.id  # Ответ на сообщение
    else:
        return message.from_user.id  # Просто автор сообщения


def start_bot():
    executor.start_polling(dp)
