# bot.py

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


class ChatParserBot:
    def __init__(self, token: str, admin_chat_id: int):
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.subscribers = set()  # chat_id клиентов
        self.admin_chat_id = admin_chat_id  # chat_id руководителя
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация всех хэндлеров"""
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message()(self.forward_to_admin_handler)  # ловим все последующие сообщения

    async def start_handler(self, message: Message):
        chat_id = message.chat.id
        if chat_id not in self.subscribers:
            self.subscribers.add(chat_id)

        # Отправка приветствия клиенту
        await message.answer(
            'Здравствуйте! Вы написали в магазин автозапчастей GG Auto. С какого города обращаетесь?'
        )

    async def forward_to_admin_handler(self, message: Message):
        chat_id = message.chat.id

        # Проверяем, что это клиент, который уже нажал /start
        if chat_id in self.subscribers:
            # Пересылаем сообщение **только одному пользователю (админу)**
            await self.bot.send_message(
                self.admin_chat_id,
                f"Сообщение от {chat_id}:\n{message.text}"
            )
