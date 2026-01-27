# user_data.py

import os
from pathlib import Path
import json

# Получаем текущую директорию (где лежит этот файл)
CURRENT_DIR = Path(__file__).resolve().parent

# Формируем пути
USER_DATA_DIR = CURRENT_DIR / 'data' / 'users'
SESSION_DATA_DIR = CURRENT_DIR / 'data' / 'sessions'

# Создаём директории при необходимости
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Функция для получения пути к файлу пользователя
def get_user_path(chat_id):
    return USER_DATA_DIR / f'{chat_id}.json'


# Функция для получения пути к сессии
def get_session_path(chat_id):
    session_name = 'chat_parser_session'
    return SESSION_DATA_DIR / f'{session_name}_{chat_id}'

