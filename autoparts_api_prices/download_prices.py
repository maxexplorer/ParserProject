# download_prices.py

import imaplib
import email
import os
import re

from email.header import decode_header

from config import (
    IMAP_SERVER,
    IMAP_PORT,
    MAILBOX,
    EMAIL_LOGIN,
    EMAIL_PASSWORD,
    KEYWORDS,
    SENDERS,
    SAVE_BASE_PATH,
    ALLOWED_EXTS
)


# ---------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------

def decode_mime(value: str) -> str:
    if not value:
        return ""
    result = ""
    for text, enc in decode_header(value):
        if isinstance(text, bytes):
            result += text.decode(enc or "utf-8", errors="ignore")
        else:
            result += text
    return result


def safe_name(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", text).strip()


# ---------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------

def extract_valid_attachments(msg):
    result = []

    for part in msg.walk():
        filename = part.get_filename()
        if not filename:
            continue

        filename = decode_mime(filename).lower()
        ext = os.path.splitext(filename)[1]

        if ext not in ALLOWED_EXTS:
            continue

        if not any(k in filename for k in KEYWORDS):
            continue

        payload = part.get_payload(decode=True)
        if payload:
            result.append((filename, payload))

    return result


def find_latest_valid_email(mail, sender: str):
    status, data = mail.search(None, f'(FROM "{sender}")')
    if status != "OK":
        return None

    ids = data[0].split()
    if not ids:
        return None

    for msg_id in reversed(ids):
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])

        if extract_valid_attachments(msg):
            return msg

    return None


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def download_prices():
    os.makedirs(SAVE_BASE_PATH, exist_ok=True)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
    mail.select(MAILBOX)

    for sender, company in SENDERS.items():
        print(f"\n--- {company} ---")

        msg = find_latest_valid_email(mail, sender)
        if not msg:
            print("Нет писем")
            continue

        attachments = extract_valid_attachments(msg)
        if not attachments:
            print("Нет вложений")
            continue

        for filename, payload in attachments:
            ext = os.path.splitext(filename)[1]
            out_name = f"{company}{ext}"
            out_path = os.path.join(SAVE_BASE_PATH, safe_name(out_name))

            with open(out_path, "wb") as f:
                f.write(payload)

            print("SAVED:", out_path)

    mail.logout()


if __name__ == "__main__":
    download_prices()