import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

MSK_TZ = ZoneInfo("Europe/Moscow")

def safe_dir_name(name: str) -> str:
    # Убираем запрещённые для Windows символы, пробелы оставляем
    name = re.sub(r'[<>:"/\\|?*]+', "_", name).strip()
    return name

def email_msk_stamp(msg) -> str:
    """
    Возвращает 'YYYY.MM.DD HH:MM' по времени Москвы на основе заголовка Date.
    """
    date_hdr = msg.get("Date", "")
    dt = parsedate_to_datetime(date_hdr)  # умеет парсить RFC-дату письма
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    dt_msk = dt.astimezone(MSK_TZ)
    return dt_msk.strftime("%Y.%m.%d %H:%M")

# === НАСТРОЙКИ ===
LOGIN = "info.gg-auto@ya.ru"
IMAP_SERVER = "imap.yandex.ru"
IMAP_PORT = 993
MAILBOX = "INBOX"
KEYWORDS = ["прайс", "price", "наличие", "остатки"]

SENDERS = [
    "sale@avtomedon-m.ru",
    "price@atbcom.ru",
    "alx@acscom.ru",
    "parts-sehun@yandex.ru",
    "vladimir@dominant-auto.ru",
    "tehnoplast77@mail.ru",
    "info@bampik.ru",
    "info@rtgrus.com"

]

COMPANIES = {
    "sale@avtomedon-m.ru": "Автомедон",
    "price@atbcom.ru": "ATБ",
    "alx@acscom.ru": "Легион",
    "parts-sehun@yandex.ru": "Сехун",
    "vladimir@dominant-auto.ru": "Сокол-авто",
    "tehnoplast77@mail.ru": "Технопласт",
    "info@bampik.ru": "ИП Рыбаков",
    "info@rtgrus.com": "Авто-парти"
}

SAVE_BASE_PATH = r"C:\Users\73278\OneDrive\Рабочий стол\onedrive\новая\OneDrive\GG Auto\РОБОКАМА\autoparts_api_prices\prices"

ALLOWED_EXTS = {".xlsx", ".xls", ".xlsm", ".xlsb", ".csv", ".tsv", ".ods"}
PASSWORD_ENV_VAR = "GG_MAIL_PASSWORD"


def decode_mime(s: str) -> str:
    if not s:
        return ""
    out = ""
    for text, enc in decode_header(s):
        if isinstance(text, bytes):
            out += text.decode(enc or "utf-8", errors="replace")
        else:
            out += text
    return out


def safe_folder_name(addr: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", addr)


def safe_filename(name: str) -> str:
    name = name.replace("/", "_").replace("\\", "_").strip()
    return re.sub(r'[<>:"/\\|?*]+', "_", name)


def clear_folder(folder: str):
    if not os.path.isdir(folder):
        return
    for fn in os.listdir(folder):
        path = os.path.join(folder, fn)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                print("WARN: cannot delete", path, "->", e)


def extract_allowed_attachments(msg):
    found = []

    for part in msg.walk():
        filename = part.get_filename()
        if not filename:
            continue

        filename = decode_mime(filename)
        filename_lower = filename.lower()

        # Проверка расширения
        ext = os.path.splitext(filename_lower)[1]
        if ext not in ALLOWED_EXTS:
            continue

        # 🔥 ФИЛЬТР ПО НАЗВАНИЮ
        if not any(word in filename_lower for word in KEYWORDS):
            continue

        payload = part.get_payload(decode=True)
        if payload:
            found.append((filename, payload))

    return found

def find_latest_message_with_allowed(mail, sender: str):
    # Ищем письма от отправителя
    status, data = mail.search(None, f'(FROM "{sender}")')
    if status != "OK":
        print("SEARCH failed:", sender, status)
        return None

    ids = data[0].split() if data and data[0] else []
    if not ids:
        return None

    # От новых к старым — первое письмо, где есть нужное вложение
    for msg_id in reversed(ids):
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        if extract_allowed_attachments(msg):
            return msg_id, msg

    return None


def main():
    password = "tkarmjpxweuqniae"

    os.makedirs(SAVE_BASE_PATH, exist_ok=True)
    print("SAVE_BASE_PATH:", os.path.abspath(SAVE_BASE_PATH))

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(LOGIN, password)

    # КРИТИЧНО: выбираем папку -> иначе будет state AUTH и SEARCH упадёт
    status, _ = mail.select(MAILBOX)
    if status != "OK":
        raise RuntimeError(f"Не удалось открыть {MAILBOX}. status={status}")

    for sender in SENDERS:
        print("\n---", sender, "---")
        result = find_latest_message_with_allowed(mail, sender)
        if not result:
            print("Не найдено писем с табличными вложениями.")
            continue

        _, msg = result
        subject = decode_mime(msg.get("Subject", ""))
        date_hdr = msg.get("Date", "")
        print("Latest subject:", subject)
        print("Email date:", date_hdr)

        attachments = extract_allowed_attachments(msg)
        if not attachments:
            print("Письмо найдено, но вложения не извлеклись (редко).")
            continue

        company = COMPANIES.get(sender, sender)  # если не нашли — папка будет email
        out_dir = os.path.join(SAVE_BASE_PATH, safe_dir_name(company))
        os.makedirs(out_dir, exist_ok=True)

        # Удаляем старые — оставляем только последние
        clear_folder(out_dir)

        company = COMPANIES.get(sender, sender)  # если нет в словаре — будет email
        msk_stamp = email_msk_stamp(msg)

        for fn, payload in attachments:
            ext = os.path.splitext(fn)[1].lower()  # сохранить исходное расширение
            out_name = f"{company}{ext}"
            out_path = os.path.join(out_dir, safe_filename(out_name))

            with open(out_path, "wb") as f:
                f.write(payload)

            print("SAVED:", out_path)

    mail.logout()


if __name__ == "__main__":
    main()