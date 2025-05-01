# bot.py

import re
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats, update_exceptions


class ChatParserBot:
    def __init__(self, token: str):
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.active_parsers = {}
        self._register_handlers()  # Регистрация обработчиков


    def _register_handlers(self):
        """Регистрация всех хэндлеров"""
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(
            F.text.startswith("+") &
            ~F.text.lower().startswith("+чат") &
            ~F.text.lower().startswith("+стоп")
        )(self.add_keywords_handler)
        self.dp.message(
            F.text.startswith("-") &
            ~F.text.lower().startswith("-чат") &
            ~F.text.lower().startswith("-стоп")
        )(self.remove_keywords_handler)
        self.dp.message(F.text.lower().startswith("+чат"))(self.add_chats_handler)
        self.dp.message(F.text.lower().startswith("-чат"))(self.remove_chats_handler)
        self.dp.message(F.text.lower().startswith("+стоп"))(self.add_stopwords_handler)
        self.dp.message(F.text.lower().startswith("-стоп"))(self.remove_stopwords_handler)
        self.dp.message(F.text.lower() == "спам")(self.mark_spam_handler)
        self.dp.message(F.text.lower().startswith("слова"))(self.show_keywords_handler)
        self.dp.message(F.text.lower().startswith("чаты"))(self.show_chats_handler)

    def process_chat_url(self, chat_url: str) -> str:
        """Обрабатывает URL чата, убирая ненужные части."""
        return chat_url.strip().replace("https://t.me/", "").replace("@", "")

    async def start_handler(self, message: Message):
        chat_id = str(message.chat.id)

        if chat_id in self.active_parsers:
            await message.answer("ℹ️ Парсер уже запущен.")
            return

        await message.answer("Привет! Я бот для мониторинга сообщений.")

        user_data = load_user_data(chat_id)
        parser = TelegramKeywordParser(
            keywords=user_data.get("keywords", []),
            stopwords=user_data.get("stopwords", []),
            chats=user_data.get("chats", []),
            exceptions=user_data.get("exceptions", []),
            bot=self.bot,
            chat_id=chat_id,
            print_dialogs=False
        )

        self.active_parsers[chat_id] = parser
        asyncio.create_task(parser.run())  # Запуск парсера в фоне

    async def add_keywords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        raw_text = message.text[1:]

        keywords = [kw.strip().strip('"\'').lower() for kw in raw_text.split(',') if kw.strip()]
        update_keywords(chat_id, keywords, add=True)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"✅ Добавлены ключевые слова: {', '.join(keywords)}")

    async def remove_keywords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        raw_text = message.text[1:]

        keywords = [kw.strip().lower() for kw in raw_text.split(',') if kw.strip()]
        update_keywords(chat_id, keywords, add=False)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"❌ Удалены ключевые слова: {', '.join(keywords)}")

    async def add_stopwords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        raw_text = message.text[5:]

        stopwords = [kw.strip().strip('"\'').lower() for kw in raw_text.split(',') if kw.strip()]
        update_keywords(chat_id, stopwords, add=True)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"✅ Добавлены слова исключения: {', '.join(stopwords)}")

    async def remove_stopwords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        raw_text = message.text[5:]

        stopwords = [kw.strip().lower() for kw in raw_text.split(',') if kw.strip()]
        update_keywords(chat_id, stopwords, add=False)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"❌ Удалены слова исключения: {', '.join(stopwords)}")

    async def add_chats_handler(self, message: Message):
        chat_id = str(message.chat.id)
        chats = [self.process_chat_url(chat) for chat in message.text[4:].split()]
        join_chats = []

        # Пытаемся подписаться на каждый чат через Telethon
        if chat_id in self.active_parsers:
            client = self.active_parsers[chat_id].client
            for chat in chats:
                try:
                    chat_entity = await client.get_entity(chat)
                    if chat_entity:
                        await client(JoinChannelRequest(chat_entity))
                        join_chats.append(chat)
                        await asyncio.sleep(1)  # небольшая задержка, чтобы избежать флуд-лимита
                except Exception as e:
                    await message.answer(f"⚠️ Ошибка подписки на <code>{chat}</code>: {e}")
                    continue

        # Обновляем локальные данные
        update_chats(chat_id, join_chats)

        # Перезагружаем данные в парсер
        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

        await message.answer(f"📌 Добавлены и подписаны на чаты:\n{chr(10).join(join_chats)}")

    async def remove_chats_handler(self, message: Message):
        chat_id = str(message.chat.id)
        chats = [self.process_chat_url(chat) for chat in message.text[4:].split()]
        leave_chats = []

        # Пытаемся отписаться от каждого чата через Telethon
        if chat_id in self.active_parsers:
            client = self.active_parsers[chat_id].client
            for chat in chats:
                try:
                    chat_entity = await client.get_entity(chat)
                    if chat_entity:
                        await client(LeaveChannelRequest(chat_entity))
                        leave_chats.append(chat)
                        await asyncio.sleep(1)  # чтобы не попасть под лимиты
                except Exception as e:
                    await message.answer(f"⚠️ Ошибка отписки на <code>{chat}</code>: {e}")
                    continue

        # Обновляем локальные данные
        update_chats(chat_id, leave_chats, add=False)

        # Перезагружаем данные в парсер
        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

        await message.answer(f"🗑️ Удалены и отписаны от чатов:\n{chr(10).join(leave_chats)}")

    async def mark_spam_handler(self, message: Message):
        if not message.reply_to_message:
            return await message.answer("❌ Ответьте на сообщение, чтобы пометить отправителя как спам.")

        # Извлекаем сообщение, на которое мы отвечаем
        replied_message = message.reply_to_message.text

        # Регулярное выражение для поиска ID или username после "Автор: "
        sender_pattern = r"Автор:\s+(@?[\w\d]+)"  # ищем @username или просто id

        match = re.search(sender_pattern, replied_message)

        if not match:
            return await message.answer("❌ Не удалось распознать отправителя.")

        sender_value = match.group(1).lstrip("@")  # Убираем @, если оно есть

        chat_id = str(message.chat.id)

        # Обновляем исключения
        update_exceptions(chat_id, [sender_value], add=True)

        # Если парсер активен для чата, загружаем данные
        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        # Ответ пользователю
        await message.answer(f"🚫 Пользователь {sender_value} добавлен в спам.")

    async def show_keywords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        keywords = load_user_data(chat_id).get("keywords", [])
        await message.answer("🔍 Ваши ключевые слова:\n" + ("\n".join(keywords) if keywords else "❌ Нет слов."))

    async def show_chats_handler(self, message: Message):
        chat_id = str(message.chat.id)
        chats = load_user_data(chat_id).get("chats", [])
        await message.answer("📂 Ваши чаты:\n" + ("\n".join(chats) if chats else "❌ Нет чатов."))
