# parser.py

import asyncio
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # <-- Добавлено
from configs.config import token
from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats, update_exceptions

bot = Bot(
    token=token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # <-- Новый формат
)
dp = Dispatcher()

active_parsers = {}


def process_chat_url(chat_url: str) -> str:
    """Обрабатывает URL чата, убирая ненужные части."""
    return chat_url.strip().replace("https://t.me/", "").replace("@", "")


@dp.message(Command("start"))
async def start(message: Message):
    chat_id = str(message.chat.id)
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
    asyncio.create_task(parser.run())  # Запуск парсера в фоне


@dp.message(F.text.startswith("+") & ~F.text.startswith("+чат"))
async def add_keywords(message: Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=True)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

    await message.answer(f"✅ Добавлены ключевые слова: {', '.join(keywords)}")


@dp.message(F.text.startswith("-") & ~F.text.startswith("-чат"))
async def remove_keywords(message: Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=False)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

    await message.answer(f"❌ Удалены ключевые слова: {', '.join(keywords)}")


@dp.message(F.text.lower().startswith("+чат"))
async def add_chats(message: Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[4:].split()]

    # Пытаемся подписаться на каждый чат через Telethon
    if chat_id in active_parsers:
        client = active_parsers[chat_id].client
        for chat in chats:
            try:
                chat_entity = await client.get_entity(chat)
                if chat_entity:
                    await client(JoinChannelRequest(chat_entity))
                    await asyncio.sleep(1)  # небольшая задержка, чтобы избежать флуд-лимита
            except Exception as e:
                print(f"⚠️ Ошибка подписки на {chat}: {e}")

    # Обновляем локальные данные
    update_chats(chat_id, chats)

    # Перезагружаем данные в парсер
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"📌 Добавлены и подписаны на чаты:\n{chr(10).join(chats)}")


@dp.message(F.text.lower().startswith("-чат"))
async def remove_chats(message: Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[5:].split()]

    # Пытаемся отписаться от каждого чата через Telethon
    if chat_id in active_parsers:
        client = active_parsers[chat_id].client
        for chat in chats:
            try:
                chat_entity = await client.get_entity(chat)
                if chat_entity:
                    await client(LeaveChannelRequest(chat_entity))
                    await asyncio.sleep(1)  # чтобы не попасть под лимиты
            except Exception as e:
                print(f"⚠️ Ошибка отписки от {chat}: {e}")

    # Обновляем локальные данные
    update_chats(chat_id, chats, add=False)

    # Перезагружаем данные в парсер
    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"🗑️ Удалены и отписаны от чатов:\n{chr(10).join(chats)}")


@dp.message(F.text.lower() == "спам")
async def mark_spam(message: Message):
    if not message.reply_to_message:
        return await message.answer("❌ Ответьте на сообщение, чтобы пометить отправителя как спам.")

    spam_sender_id = message.reply_to_message.from_user.id
    chat_id = str(message.chat.id)
    update_exceptions(chat_id, [spam_sender_id], add=True)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

    await message.answer(f"🚫 Пользователь {spam_sender_id} добавлен в исключения.")


@dp.message(F.text.lower().startswith("слова"))
async def show_keywords(message: Message):
    chat_id = str(message.chat.id)
    keywords = load_user_data(chat_id).get("keywords", [])
    await message.answer("🔍 Ваши ключевые слова:\n" + ("\n".join(keywords) if keywords else "❌ Нет слов."))


@dp.message(F.text.lower().startswith("чаты"))
async def show_chats(message: Message):
    chat_id = str(message.chat.id)
    chats = load_user_data(chat_id).get("chats", [])
    await message.answer("📂 Ваши чаты:\n" + ("\n".join(chats) if chats else "❌ Нет чатов."))


async def main():
    await dp.start_polling(bot)
