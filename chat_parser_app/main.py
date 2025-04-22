import asyncio

from parser import TelegramKeywordParser
from bot import start_bot  # Импортируем запуск бота


if __name__ == "__main__":
    # try:
    #     with open('data/chats.txt', 'r', encoding='utf-8') as file:
    #         chats = [line.strip() for line in file.readlines()]
    # except FileNotFoundError as ex:
    #     raise ex
    #
    # try:
    #     with open('data/keywords.txt', 'r', encoding='utf-8') as file:
    #         keywords = [line.strip() for line in file.readlines()]
    # except FileNotFoundError as ex:
    #     raise ex
    #
    # parser = TelegramKeywordParser(keywords=keywords, chats=chats, bot=bot)
    # asyncio.run(parser.run())


    async def main():
        await start_bot()  # Асинхронно запускаем функцию start_bot()


    if __name__ == "__main__":
        asyncio.run(main())  # Запускаем асинхронную main функцию

