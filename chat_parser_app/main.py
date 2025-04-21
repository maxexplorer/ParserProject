import asyncio
from parser import TelegramKeywordParser


if __name__ == "__main__":
    try:
        with open('data/chats.txt', 'r', encoding='utf-8') as file:
            chats = [line.strip() for line in file.readlines()]
    except FileNotFoundError as ex:
        raise ex

    try:
        with open('data/keywords.txt', 'r', encoding='utf-8') as file:
            keywords = [line.strip() for line in file.readlines()]
    except FileNotFoundError as ex:
        raise ex

    parser = TelegramKeywordParser(keywords, chats)
    asyncio.run(parser.run())