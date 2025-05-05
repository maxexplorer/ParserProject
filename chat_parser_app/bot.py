# bot.py

import re
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats, update_stopwords, update_exceptions


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
        self.dp.message(F.text.lower().startswith("исключения"))(self.show_stopwords_handler)

    @staticmethod
    def process_chat_url(chat_url: str) -> tuple[str, str]:
        """
        Возвращает тип ('invite' или 'public') и очищенный идентификатор.
        """
        chat_url = chat_url.strip()
        if 'joinchat/' in chat_url:
            return 'invite', chat_url.split('joinchat/')[-1]
        if '"/+"' in chat_url or chat_url.startswith('+'):
            return 'invite', chat_url.split('/')[-1].lstrip('+')
        return 'public', chat_url.replace('https://t.me/', '').replace('@', '')

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
        update_stopwords(chat_id, stopwords, add=True)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"✅ Добавлены слова исключения: {', '.join(stopwords)}")

    async def remove_stopwords_handler(self, message: Message):
        chat_id = str(message.chat.id)
        raw_text = message.text[5:]

        stopwords = [kw.strip().lower() for kw in raw_text.split(',') if kw.strip()]
        update_stopwords(chat_id, stopwords, add=False)

        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(load_user_data(chat_id))

        await message.answer(f"❌ Удалены слова исключения: {', '.join(stopwords)}")

    async def add_chats_handler(self, message: Message):
        chat_id = str(message.chat.id)
        chat_inputs = [self.process_chat_url(chat) for chat in message.text[4:].split() if chat.strip()]

        join_chats = []

        if chat_id in self.active_parsers:
            client = self.active_parsers[chat_id].client

            for chat_type, chat_value in chat_inputs:
                try:
                    if chat_type == "invite":
                        await client(ImportChatInviteRequest(chat_value))
                    else:  # "public"
                        chat_entity = await client.get_entity(chat_value)
                        if chat_entity:
                            await client(JoinChannelRequest(chat_entity))

                    join_chats.append(chat_value)
                    await asyncio.sleep(3)

                except Exception as e:
                    await message.answer(f"⚠️ Ошибка подписки на <code>{chat_value}</code>: {e}")
                    continue
        # Обновляем локальные данные
        update_chats(chat_id, join_chats)

        # Перезагружаем данные в парсер
        if chat_id in self.active_parsers:
            self.active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

        if join_chats:
            await message.answer(f"📌 Добавлены и подписаны на чаты:\n" +
                                 "\n".join(f"<code>{chat}</code>" for chat in join_chats))

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

    @staticmethod
    async def show_keywords_handler(message: Message):
        chat_id = str(message.chat.id)
        keywords = load_user_data(chat_id).get("keywords", [])
        await message.answer("🔍 Ваши ключевые слова:\n" + ("\n".join(keywords) if keywords else "❌ Нет слов."))

    @staticmethod
    async def show_chats_handler(message: Message):
        chat_id = str(message.chat.id)
        chats = load_user_data(chat_id).get("chats", [])
        await message.answer("📂 Ваши чаты:\n" + ("\n".join(chats) if chats else "❌ Нет чатов."))

    @staticmethod
    async def show_stopwords_handler(message: Message):
        chat_id = str(message.chat.id)
        stopwords = load_user_data(chat_id).get("stopwords", [])
        await message.answer("🔍 Ваши слова исключения:\n" + ("\n".join(stopwords) if stopwords else "❌ Нет слов."))
