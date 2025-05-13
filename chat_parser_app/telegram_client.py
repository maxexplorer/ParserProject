# telegram_client.py

from telethon import TelegramClient

from configs.config import api_id, api_hash
from user_data import get_session_path

clients = {}

def get_client(chat_id: str):
    if chat_id not in clients:
        client = TelegramClient(f'{get_session_path(chat_id)}', api_id, api_hash)
        clients[chat_id] = client
    return clients[chat_id]
