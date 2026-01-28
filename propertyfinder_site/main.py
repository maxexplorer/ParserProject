# main.py

import asyncio
from datetime import datetime, time as dtime, timedelta
import os
from parser import get_data, headers
from bot import ChatParserBot
from config import BOT_TOKEN, PAGES_TO_COLLECT, DAYS_TO_COLLECT, BATCH_SIZE, RESULTS_DIR
from logger import logger

async def run_parser(bot: ChatParserBot):
    """Сбор данных и отправка Excel подписчикам"""
    logger.info("Запуск парсера...")
    get_data(headers=headers, pages=PAGES_TO_COLLECT, days=DAYS_TO_COLLECT, batch_size=BATCH_SIZE)

    today_str = datetime.today().strftime("%d-%m-%Y")
    file_path = os.path.join(RESULTS_DIR, f"result_data_{today_str}.xlsx")

    if os.path.exists(file_path):
        await bot.send_excel_to_subscribers(file_path)
    else:
        logger.warning("Файл Excel не найден для отправки.")

async def parser_scheduler(bot: ChatParserBot, target_time: dtime):
    """Запуск парсера в заданное время каждый день"""
    while True:
        now = datetime.now()
        next_run = datetime.combine(now.date(), target_time)
        if next_run < now:
            next_run += timedelta(days=1)  # если время уже прошло сегодня, берём завтра
        wait_seconds = (next_run - now).total_seconds()

        logger.info(f"Следующий запуск парсера в {next_run}. Ждём {wait_seconds:.0f} секунд...")
        await asyncio.sleep(wait_seconds)

        # Запуск парсера
        await run_parser(bot)

async def main():
    bot_instance = ChatParserBot(token=BOT_TOKEN)
    await bot_instance.bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бота в фоне
    bot_task = asyncio.create_task(bot_instance.dp.start_polling(bot_instance.bot))

    # Запускаем scheduler парсера (например, в 09:00)
    parser_task = asyncio.create_task(parser_scheduler(bot_instance, target_time=dtime(19, 00)))

    # Ждём завершения обоих (бот не завершится сам)
    await asyncio.gather(bot_task, parser_task)

if __name__ == "__main__":
    asyncio.run(main())
