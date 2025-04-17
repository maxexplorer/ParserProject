from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from configs.config import api_id, api_hash, session_name, results_file
import asyncio
import os


class TelegramKeywordParser:
    def __init__(self, keywords: list[str], target_chats: list[str]):
        self.keywords = [kw.lower() for kw in keywords]
        self.target_chats = target_chats
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def run(self):
        async with self.client:
            print("[✓] Успешное подключение к Telegram")

            print("\n[→] Список всех доступных чатов:")
            async for dialog in self.client.iter_dialogs():
                print(f"- {dialog.name} | ID: {dialog.id} | Username: {getattr(dialog.entity, 'username', None)}")

            print("\n[→] Поиск сообщений...\n")
            for chat in self.target_chats:
                await self._process_chat(chat)

    async def _process_chat(self, chat):
        print(f"\n[→] Поиск в чате: {chat}")
        try:
            entity = await self.client.get_entity(chat)
        except Exception as e:
            print(f"[!] Ошибка получения чата {chat}: {e}")
            return

        count = 0
        async for message in self.client.iter_messages(entity, limit=100):  # можешь увеличить лимит
            if message.message:
                msg_text = message.message.lower()
                if any(keyword in msg_text for keyword in self.keywords):
                    count += 1
                    self._save_result(chat, message)
        print(f"[✓] Найдено сообщений: {count}")

    def _save_result(self, chat, message):
        os.makedirs(os.path.dirname(results_file), exist_ok=True)

        sender = getattr(message.sender, 'username', None)
        sender_id = message.sender_id or "—"
        chat_title = getattr(message.chat, 'title', chat)

        entity = message.chat
        chat_username = getattr(entity, 'username', None)
        chat_link = f"https://t.me/{chat_username}" if chat_username else None
        message_link = (
            f"https://t.me/{chat_username}/{message.id}"
            if chat_username
            else f"https://t.me/c/{str(entity.id)[4:]}/{message.id}"
        )
        user_link = f"@{sender}" if sender else f"ID: {sender_id}"
        date_time = message.date.astimezone().strftime("%Y-%m-%d %H:%M:%S")

        chat_line = f'Чат: <a href="{chat_link}">{chat_title}</a>' if chat_link else f"Чат: {chat_title}"

        formatted = (
            f"{chat_line}\n"
            f"Автор: {user_link}\n"
            f"Дата: {date_time}\n"
            f"Ссылка: <a href=\"{message_link}\">{message_link}</a>\n"
            f"Сообщение:\n{message.text}\n\n"
            f"--------------------\n\n"
        )

        with open(results_file, 'a', encoding='utf-8') as f:
            f.write(formatted)
