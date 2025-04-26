import os

import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telethon import TelegramClient
from configs.config import token, api_id, api_hash, session_name
from parser import TelegramKeywordParser
from user_data import load_user_data, update_keywords, update_chats

# FSM состояния для авторизации
class AuthStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_password = State()

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

active_parsers = {}

def process_chat_url(chat_url):
    return chat_url.strip().replace("https://t.me/", "").lstrip("@")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    chat_id = str(message.chat.id)
    session_path = f"{session_name}_{chat_id}.session"
    if not os.path.exists(session_path):
        await message.answer("Для начала работы нужно авторизоваться.\nНапиши или нажмите:\n/login")
        return

    await message.answer("Привет! Я бот для мониторинга сообщений.")

    user_data = load_user_data(chat_id)
    parser = TelegramKeywordParser(
        keywords=user_data.get("keywords", []),
        chats=user_data.get("chats", []),
        bot=bot,
        chat_id=chat_id
    )
    active_parsers[chat_id] = parser
    asyncio.create_task(parser.run())


# === АВТОРИЗАЦИЯ ===

@dp.message_handler(commands=["login"])
async def login_command(message: types.Message):
    chat_id = str(message.chat.id)
    session_path = f"{session_name}_{chat_id}.session"
    if os.path.exists(session_path):
        await message.answer("Вы уже авторизованы.")
        return
    await message.answer("Введите номер телефона (в формате +7.......):")
    await AuthStates.waiting_for_phone.set()


@dp.message_handler(state=AuthStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    chat_id = str(message.chat.id)
    client = TelegramClient(f"{session_name}_{chat_id}", api_id, api_hash)
    await client.connect()

    try:
        await client.send_code_request(phone)
        await state.update_data(phone=phone, client=client)
        await message.answer("Введите код, отправленный Вам в Telegram:")
        await AuthStates.waiting_for_code.set()
    except Exception as e:
        await message.answer(f"Ошибка при отправке кода: {e}")
        await state.finish()


@dp.message_handler(state=AuthStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    client = data["client"]
    phone = data["phone"]

    try:
        await client.sign_in(phone=phone, code=code)
        await message.answer("Успешно авторизовано! ✅ Теперь отправь /start.")
        await state.finish()
    except Exception as e:
        if "password" in str(e).lower():
            await message.answer("Введите пароль от облака (2FA):")
            await AuthStates.waiting_for_password.set()
        else:
            await message.answer(f"Ошибка входа: {e}")
            await state.finish()


@dp.message_handler(state=AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    client = data["client"]

    try:
        await client.sign_in(password=password)
        await message.answer("Авторизация прошла успешно! ✅ Теперь отправь /start.")
    except Exception as e:
        await message.answer(f"Ошибка при вводе пароля: {e}")
    await state.finish()


# === ОБРАБОТКА КЛЮЧЕВЫХ СЛОВ И ЧАТОВ ===

@dp.message_handler(lambda msg: msg.text.startswith("+") and not msg.text.startswith("+чат"))
async def add_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=True)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Добавлены ключевые слова: {', '.join(keywords)}")


@dp.message_handler(lambda msg: msg.text.startswith("-") and not msg.text.startswith("-чат"))
async def remove_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    keywords = [kw.strip().lower() for kw in message.text[1:].split()]
    update_keywords(chat_id, keywords, add=False)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Удалены ключевые слова: {', '.join(keywords)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("+чат"))
async def add_chats(message: types.Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[4:].split()]
    update_chats(chat_id, chats)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Добавлены чаты: {', '.join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("-чат"))
async def remove_chats(message: types.Message):
    chat_id = str(message.chat.id)
    chats = [process_chat_url(chat) for chat in message.text[5:].split()]
    update_chats(chat_id, chats, add=False)

    if chat_id in active_parsers:
        active_parsers[chat_id].load_data_from_file(user_data=load_user_data(chat_id))

    await message.answer(f"Удалены чаты: {', '.join(chats)}")


@dp.message_handler(lambda msg: msg.text.lower().startswith("показать слова"))
async def show_keywords(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    keywords = user_data.get("keywords", [])
    if keywords:
        await message.answer(f"Ключевые слова:\n{chr(10).join(keywords)}")
    else:
        await message.answer("У вас нет добавленных ключевых слов.")


@dp.message_handler(lambda msg: msg.text.lower().startswith("показать чаты"))
async def show_chats(message: types.Message):
    chat_id = str(message.chat.id)
    user_data = load_user_data(chat_id)
    chats = user_data.get("chats", [])
    if chats:
        await message.answer(f"Чаты:\n{chr(10).join(chats)}")
    else:
        await message.answer("У вас нет добавленных чатов.")


def start_bot():
    executor.start_polling(dp, skip_updates=True)
