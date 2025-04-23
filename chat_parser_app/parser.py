from aiogram import Bot
from telethon import TelegramClient, events

from configs.config import api_id, api_hash, session_name


class TelegramKeywordParser:
    def __init__(self, keywords: list[str], chats: list[str], bot: Bot, chat_id):
        self.keywords = [kw.lower() for kw in keywords]
        self.chats = chats
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.bot = bot
        self.chat_id = chat_id

    async def run(self):
        async with self.client:
            print("\n[→] Список всех доступных чатов:")

            async for dialog in self.client.iter_dialogs():
                print(f"- {dialog.name} | ID: {dialog.id} | Username: {getattr(dialog.entity, 'username', None)}")

            print("\n[→] Поиск сообщений...\n")
            for chat in self.chats:
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
                    await self._send_result(chat, message)
        print(f"[✓] Найдено сообщений: {count}")

    async def _send_result(self, chat, message):
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
            f"Ссылка на сообщение: <a href=\"{message_link}\">Ссылка</a>\n"
            f"Сообщение:\n{message.text}\n\n"
            f"Дата: {date_time}\n"
            # f"--------------------\n\n"
        )

        # Отправляем результат в указанный чат
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=formatted, parse_mode='HTML')
        except Exception as e:
            print(f"[!] Ошибка при отправке сообщения: {e}")
