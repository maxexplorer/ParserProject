import asyncio
from bot import ChatParserBot
from configs.config import token


async def main():
    bot = ChatParserBot(token=token)

    # 🔥 ВАЖНО: удалить webhook перед polling
    await bot.bot.delete_webhook(drop_pending_updates=True)

    await bot.dp.start_polling(bot.bot)


if __name__ == '__main__':
    asyncio.run(main())
