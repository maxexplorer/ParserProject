# bot.py

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties



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


    async def start_handler(self, message: Message):
        chat_id = str(message.chat.id)

        if chat_id in self.active_parsers:
            await message.answer('ℹ️ Парсер уже запущен.')
            return

        await message.answer('Привет! Я бот для мониторинга сообщений.')


