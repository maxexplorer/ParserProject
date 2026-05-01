import os
import re
import glob
import requests
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, SSLError


# =======================
# CONFIG
# =======================

FOLDER: str = "data"
OUTPUT_FILE: str = "result.xlsx"
TIMEOUT: int = 8
MAX_WORKERS: int = 20  # кол-во параллельных потоков

HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

PARKING_PHRASES = [
    "domain for sale",
    "buy this domain",
    "coming soon",
    "under construction",
    "domain is parked",
    "this domain is for sale",
    "прилинкуйте домен",
    "домен никуда не направлен",
    "this domain has expired",
    "renew this domain",
    "domain expired",
    "website coming soon",
    "сайт находится на обслуживании",
]

PROTECTION_SIGNATURES = [
    "just a moment",           # Cloudflare JS challenge
    "checking your browser",
    "cf_chl_opt",
    "ddos-guard",
    "please wait while we check",
    "are you human",
    "robot or human",
    "enable javascript and cookies",
    "sucuri website firewall",
    "this site is protected",
]


# =======================
# HELPERS
# =======================

def normalize_url(url: str) -> str:
    """Парсит markdown-ссылки и добавляет схему если нет."""
    url = url.strip()
    # markdown вида [text](url)
    md_match = re.match(r'\[.*?\]\((.*?)\)', url)
    if md_match:
        url = md_match.group(1).strip()
    # убираем схему — будем пробовать сами
    url = re.sub(r'^https?://', '', url)
    return url


def detect_parking(text: str) -> bool:
    text = text.lower()
    return any(p in text for p in PARKING_PHRASES)


def detect_protection(response: requests.Response) -> bool:
    """Проверяет заголовки и тело ответа на признаки защиты."""
    # заголовки
    server = response.headers.get("server", "").lower()
    if "cloudflare" in server or "ddos-guard" in server:
        return True
    if "cf-ray" in response.headers:
        return True

    # тело ответа
    text = response.text.lower()
    return any(sig in text for sig in PROTECTION_SIGNATURES)


# =======================
# CLASSIFICATION
# =======================

def _fetch(url: str, session: requests.Session):
    """Один HTTP-запрос. Возвращает Response или None."""
    try:
        return session.get(url, timeout=TIMEOUT, allow_redirects=True)
    except SSLError:
        return "ssl_error"
    except RequestException:
        return None


def classify_website(raw_url: str) -> tuple[str, str]:
    """
    Возвращает (original_url, status).
    Статусы: working | protected | not_working
    Создаёт свою сессию — безопасно для потоков.
    """
    domain = normalize_url(raw_url)

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for scheme in ("https://", "http://"):
            url = scheme + domain
            result = _fetch(url, session)

            if result is None:
                continue

            if result == "ssl_error":
                # сертификат сломан — сайт существует, но не работает
                return raw_url, "not_working"

            r: requests.Response = result

            # — Защита по коду ответа —
            if r.status_code in (401, 403, 429):
                return raw_url, "protected"

            # — Защита по содержимому (Cloudflare, WAF и т.д.) —
            if detect_protection(r):
                return raw_url, "protected"

            # — Не работает —
            if r.status_code in (404, 410):
                return raw_url, "not_working"

            if r.status_code != 200:
                return raw_url, "not_working"

            # — Парковка —
            if detect_parking(r.text):
                return raw_url, "not_working"

            # — Пустая страница —
            if len(r.text.strip()) < 300:
                return raw_url, "not_working"

            return raw_url, "working"

    # оба протокола не ответили
    return raw_url, "not_working"


# =======================
# LOAD DATA
# =======================

def load_urls_from_excels(folder: str) -> list[str]:
    files = glob.glob(os.path.join(folder, "*.xls*"))
    urls = []
    for file in files:
        df = pd.read_excel(file, sheet_name=0, header=None)
        urls.extend(df.iloc[:, 0].dropna().astype(str).tolist())
    # дедупликация с сохранением порядка
    return list(dict.fromkeys(u.strip() for u in urls if u.strip()))


# =======================
# SAVE
# =======================

def save_results(results: dict[str, list[str]]):
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for status, urls in results.items():
            pd.DataFrame({"url": urls}).to_excel(writer, sheet_name=status, index=False)


# =======================
# MAIN
# =======================

def main():
    print("Loading URLs...")
    urls = load_urls_from_excels(FOLDER)
    total = len(urls)
    print(f"Total (deduplicated): {total}")

    results: dict[str, list[str]] = {
        "working": [],
        "not_working": [],
        "protected": [],
    }

    processed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(classify_website, url): url for url in urls}

        for future in as_completed(futures):
            original_url, status = future.result()
            results[status].append(original_url)
            processed += 1

            if processed % 50 == 0 or processed == total:
                print(
                    f"{processed}/{total} | "
                    f"working: {len(results['working'])} | "
                    f"protected: {len(results['protected'])} | "
                    f"not_working: {len(results['not_working'])}"
                )

    save_results(results)
    print(f"\nDone → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()