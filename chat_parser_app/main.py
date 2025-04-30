# main.py

import asyncio
from bot import ChatParserBot
from configs.config import token


async def main():
    bot = ChatParserBot(token=token).bot
    await bot.dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
