from telethon import TelegramClient, events
from configs.config import api_id, api_hash, session_name, token, chat_id
from aiogram import Bot

class TelegramKeywordParser:
    def __init__(self, keywords: list[str], chats: list[str]):
        self.keywords = [kw.lower() for kw in keywords]
        self.chats = chats
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.bot = Bot(token=token)
        self.chat_ids = set()

    async def run(self):
        await self._resolve_chat_ids()

        @self.client.on(events.NewMessage(chats=list(self.chat_ids)))
        async def handler(event):
            message = event.message
            if message and message.message:
                lowered = message.message.lower()
                if any(keyword in lowered for keyword in self.keywords):
                    await self._send_result(message)

        print("[✓] Мониторинг новых сообщений запущен...\n")
        async with self.client:
            await self.client.run_until_disconnected()

    async def _resolve_chat_ids(self):
        async with self.client:
            for chat in self.chats:
                try:
                    entity = await self.client.get_entity(chat)
                    self.chat_ids.add(entity)
                except Exception as e:
                    print(f"[!] Не удалось получить чат {chat}: {e}")

    async def _send_result(self, message):
        sender = getattr(message.sender, 'username', None)
        sender_id = message.sender_id or "—"
        chat_title = getattr(message.chat, 'title', 'Unknown Chat')

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

        try:
            await self.bot.send_message(chat_id=chat_id, text=formatted, parse_mode='HTML')
        except Exception as e:
            print(f"[!] Ошибка при отправке сообщения: {e}")
