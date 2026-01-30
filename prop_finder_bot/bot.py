# bot.py

import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from logger import logger


class ChatParserBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self._register_handlers()
        self.subscribers = set()  # chat_id подписчиков

    def _register_handlers(self):
        self.dp.message(Command("start"))(self.start_handler)

    async def start_handler(self, message: Message):
        chat_id = message.chat.id

        if chat_id in self.subscribers:
            await message.answer("ℹ️ Парсер уже запущен.")
            return

        self.subscribers.add(chat_id)
        await message.answer("✅ Привет! Ты подписан на получение Excel с объявлениями.")

    async def send_excel_to_subscribers(self, file_path: str):
        if not self.subscribers:
            logger.info("Нет подписчиков для отправки файла.")
            return

        for chat_id in self.subscribers:
            try:
                f = FSInputFile(file_path)
                await self.bot.send_document(chat_id, f)
                logger.info(f"Файл {file_path} отправлен пользователю {chat_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить файл {file_path} пользователю {chat_id}: {e}")

        # После отправки — удаляем файл
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл {file_path} удалён после отправки.")
