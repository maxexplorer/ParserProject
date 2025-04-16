import asyncio
from parser import TelegramKeywordParser

from configs.config import keywords, target_chats

if __name__ == "__main__":
    parser = TelegramKeywordParser(keywords, target_chats)
    asyncio.run(parser.run())
