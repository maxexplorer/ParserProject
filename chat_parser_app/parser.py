# parser.py

import re
from aiogram import Bot
from telethon import TelegramClient, events
from configs.config import api_id, api_hash, session_name


class TelegramKeywordParser:
    def __init__(self, keywords, chats, bot: Bot, chat_id, exceptions, print_dialog=False):
        self.keywords = [kw.lower() for kw in keywords]
        self.chats = [chat.lower().lstrip("@") for chat in chats]
        self.exceptions = [ex for ex in exceptions]
        self.bot = bot
        self.chat_id = chat_id
        self.client = TelegramClient(f"{session_name}_{chat_id}", api_id, api_hash)
        self.print_dialog = print_dialog

    async def run(self):
        try:
            await self.client.start()
            self.client.add_event_handler(self._new_message_handler, events.NewMessage())
            print(f"[→] Парсер запущен для chat_id={self.chat_id}")

            if self.print_dialog:
                # Вызов функции для получения списка всех чатов
                await self.print_all_dialogs()

            await self.client.run_until_disconnected()
        except Exception as e:
            print(f"[!] Ошибка в парсере: {e}")
            await self.client.disconnect()

    async def _new_message_handler(self, event):
        try:
            message = event.message
            if not message.text:
                return

            # Пропускаем ботов и None-отправителей
            sender = await message.get_sender()
            if not sender or getattr(sender, 'bot', False):
                return

            # Проверка на исключения
            sender_id = sender.id
            if sender_id in self.exceptions:
                return

            msg_text = message.text.lower()
            chat = await event.get_chat()
            chat_username = getattr(chat, 'username', None)
            chat_id_str = str(event.chat_id)

            # Проверяем, что чат в списке отслеживаемых
            if (chat_username and chat_username.lower() not in self.chats) and (chat_id_str not in self.chats):
                return

            # Проверяем ключевые слова
            if any(re.search(rf'\b{re.escape(kw)}\b', msg_text) for kw in self.keywords):
                await self._send_result(event.chat_id, message)
        except Exception as e:
            print(f"[!] Ошибка обработки сообщения: {e}")

    async def _send_result(self, chat_id, message):
        try:
            sender = await message.get_sender()
            chat = await message.get_chat()

            sender_username = getattr(sender, 'username', None)
            sender_id = sender.id if sender else '—'
            chat_title = getattr(chat, 'title', str(chat_id))
            chat_username = getattr(chat, 'username', None)

            chat_link = f"https://t.me/{chat_username}" if chat_username else None
            message_link = (
                f"https://t.me/{chat_username}/{message.id}"
                if chat_username else f"https://t.me/c/{str(chat.id)[4:]}/{message.id}"
            )
            user_link = f"@{sender_username}" if sender_username else f"ID: {sender_id}"

            chat_line = f'Чат: <a href="{chat_link}">{chat_title}</a>' if chat_link else f"Чат: {chat_title}"

            formatted = (
                f"{chat_line}\n"
                f"Автор: {user_link}\n"
                f"Ссылка: <a href=\"{message_link}\">Сообщение</a>\n"
                f"Текст:\n{message.text}\n\n"
            )

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted,
                disable_web_page_preview=True,  # Убирает превью ссылки
                parse_mode="HTML"  # Если нужно форматирование HTML
            )
        except Exception as e:
            print(f"[!] Ошибка отправки уведомления: {e}")

    async def print_all_dialogs(self):
        """Функция для вывода всех доступных чатов"""
        print("\n[→] Список всех доступных чатов:")
        async for dialog in self.client.iter_dialogs():
            chat = dialog.entity
            chat_username = getattr(chat, 'username', None)
            chat_name = dialog.name
            chat_id = dialog.id
            print(f"- {chat_name} | ID: {chat_id} | Username: {chat_username or '—'}")

    def load_data_from_file(self, user_data):
        """Обновляет данные из файла"""
        self.keywords = [kw.lower() for kw in user_data.get("keywords", [])]
        self.chats = [chat.lower().lstrip("@") for chat in user_data.get("chats", [])]
        self.exceptions = user_data.get("exceptions", [])
