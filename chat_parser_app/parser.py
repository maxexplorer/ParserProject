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
                    self._save_result(chat, message.text)
        print(f"[✓] Найдено сообщений: {count}")

    def _save_result(self, chat, text):
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'a', encoding='utf-8') as f:
            f.write(f"[{chat}]\n{text}\n\n")
