# user_data.py

import os
import json

USER_DATA_DIR = "data/users"

os.makedirs(USER_DATA_DIR, exist_ok=True)


def get_user_file(chat_id):
    return os.path.join(USER_DATA_DIR, f"{chat_id}.txt")


def load_user_data(chat_id):
    file_path = get_user_file(chat_id)
    if not os.path.exists(file_path):
        return {"keywords": [], "chats": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_user_data(chat_id, data):
    with open(get_user_file(chat_id), "w", encoding="utf-8") as f:
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


def update_chats(chat_id, chats, add=True):
    data = load_user_data(chat_id)
    current = set(data.get("chats", []))

    if add:
        current.update(chats)
    else:
        current.difference_update(chats)

    data["chats"] = list(current)
    save_user_data(chat_id, data)

