import asyncio
from aiogram.types import BotCommand

from bot import ChatParserBot
from config import token


ADMIN_CHAT_ID = 469984781  # сюда ставишь chat_id руководителя

async def main():
    bot = ChatParserBot(token=token, admin_chat_id=ADMIN_CHAT_ID)

    # Удаляем старый webhook
    await bot.bot.delete_webhook(drop_pending_updates=True)

    # 🔹 Явно задаём команды бота (только те, что нужны)
    await bot.bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
    ])

    await bot.dp.start_polling(bot.bot)

if __name__ == '__main__':
    asyncio.run(main())
