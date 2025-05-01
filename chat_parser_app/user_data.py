# user_data.py

import os
from pathlib import Path
import json

# Получаем текущую директорию (где лежит этот файл)
CURRENT_DIR = Path(__file__).resolve().parent

# Формируем пути
USER_DATA_DIR = CURRENT_DIR / "data" / "users"
SESSION_DATA_DIR = CURRENT_DIR / "data" / "sessions"

# Создаём директории при необходимости
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Функция для получения пути к файлу пользователя
def get_user_path(chat_id):
    return USER_DATA_DIR / f"{chat_id}.json"


# Функция для получения пути к сессии
def get_session_path(chat_id):
    session_name = 'chat_parser_session'
    return SESSION_DATA_DIR / f"{session_name}_{chat_id}"


def load_user_data(chat_id):
    file_path = get_user_path(chat_id)
    if not os.path.exists(file_path):
        return {"keywords": [], "stopwords": [], "chats": [], "exceptions": []}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # На случай, если старый файл без "exceptions" и "stopwords"
    if "exceptions" not in data:
        data["exceptions"] = []
    if "stopwords" not in data:
        data["stopwords"] = []
    return data


def save_user_data(chat_id, data):
    with open(get_user_path(chat_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def update_keywords(chat_id, keywords, add=True):
    data = load_user_data(chat_id)
    current = set(data.get("keywords", []))
    if add:
        current.update(keywords)
    else:
        current.difference_update(keywords)
    data["keywords"] = list(current)
    save_user_data(chat_id, data)

def update_stopwords(chat_id, stopwords, add=True):
    data = load_user_data(chat_id)
    current = set(data.get("stopwords", []))
    if add:
        current.update(stopwords)
    else:
        current.difference_update(stopwords)
    data["stopwords"] = list(current)
    save_user_data(chat_id, data)


def update_chats(chat_id, chats, add=True):
    data = load_user_data(chat_id)
    current = set(data.get("chats", []))

    if add:
        current.update(chats)
    else:
        current.difference_update(chats)

    data["chats"] = list(current)
    save_user_data(chat_id, data)


def update_exceptions(chat_id, user_ids, add=True):
    data = load_user_data(chat_id)
    current = set(data.get("exceptions", []))
    if add:
        current.update(user_ids)
    else:
        current.difference_update(user_ids)
    data["exceptions"] = list(current)
    save_user_data(chat_id, data)
