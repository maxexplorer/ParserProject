import os
import re
import glob
import requests
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException, SSLError

start_time = datetime.now()

# =======================
# CONFIG
# =======================

TIMEOUT: int = 8
MAX_WORKERS: int = 20

HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# HTTP-коды, которые означают защиту
PROTECTED_CODES = {401, 403, 429}

# HTTP-коды, которые означают "не работает"
DEAD_CODES = {404, 410, 500, 502, 503, 504}

# Фразы-маркеры парковки/заглушки — дополнительный фильтр
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
    "domain parking",
    "parked domain",
    "домен не прилинкован",
    "не прилинкован ни к одной",
]

# Стоп-слова — нежелательная тематика
EXCLUDED_PHRASES = [
    # казино / ставки
    "казино", "casino", "слоты", "slots", "рулетка", "roulette",
    "ставки", "букмекер", "bets", "betting", "покер", "poker",
    "джекпот", "jackpot", "игровые автоматы", "spin",
    # крипто-скам
    "криптовалюта", "bitcoin", "btc", "ethereum",
    "пассивный доход", "торговый робот",
    # 18+ / порно
    "порно", "porno", "xxx", "porn", "секс видео", "sex video",
    "эротика", "erotica", "nude", "голые", "онлифанс", "onlyfans",
    # эскорт
    "эскорт", "escort", "интим", "dosug",
    # пиратские фильмы / сериалы
    "смотреть онлайн", "смотреть бесплатно", "смотреть фильм",
    "смотреть сериал", "lordfilm", "lordserial", "kinopoisk",
    "kinogo", "rezka", "hdrezka", "filmix", "seasonvar",
    "все серии", "новая серия", "в хорошем качестве",
    "hd 720", "hd 1080", "fullhd",
]

# Стоп-домены в ссылках (партнёрки казино/букмекеров)
EXCLUDED_LINK_DOMAINS = [
    "1xbet", "melbet", "mostbet", "vulkan", "pin-up",
    "betcity", "fonbet", "parimatch",
]


# =======================
# HELPERS
# =======================

def normalize_url(url: str) -> str:
    """Парсит markdown-ссылки и убирает схему."""
    url = url.strip()
    md_match = re.match(r'\[.*?\]\((.*?)\)', url)
    if md_match:
        url = md_match.group(1).strip()
    url = re.sub(r'^https?://', '', url)
    return url


def get_root_domain(domain: str) -> str:
    """Возвращает корневой домен без www и субдоменов."""
    domain = domain.lower().split("/")[0]
    parts = domain.split(".")
    # берём последние две части: example.ru
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain


def detect_parking(text: str) -> bool:
    """Проверяет текст страницы на явные маркеры парковки."""
    text = text.lower()
    return any(phrase in text for phrase in PARKING_PHRASES)


def is_excluded_content(html: str) -> bool:
    """Проверяет страницу на нежелательную тематику."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "svg"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True).lower()

    if any(phrase in text for phrase in EXCLUDED_PHRASES):
        return True

    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"].lower()
        if any(domain in href for domain in EXCLUDED_LINK_DOMAINS):
            return True

    return False


def is_alive(html: str, domain: str) -> bool:
    """
    Скоринг признаков живого сайта.
    Проверяет принадлежность контента домену, а не хостингу.
    """
    soup = BeautifulSoup(html, "lxml")
    domain_root = domain.lower().split("/")[0]

    for tag in soup(["script", "style", "svg"]):
        tag.decompose()

    score = 0

    # 1. Объём реального текста
    text = soup.get_text(separator=" ", strip=True)
    if len(text) > 1000:
        score += 2

    # 2. Ссылки ведут на ЭТОТ домен или относительные пути
    links = soup.find_all("a", href=True)
    own_links = [
        l for l in links
        if domain_root in l["href"] or l["href"].startswith("/")
    ]
    if len(own_links) >= 3:
        score += 2

    # 3. Ресурсы (CSS/JS) принадлежат ЭТОМУ домену
    scripts = soup.find_all("script", src=True)
    styles = soup.find_all("link", rel="stylesheet")
    own_resources = [
        r for r in scripts + styles
        if domain_root in r.get("src", "") + r.get("href", "")
    ]
    if len(own_resources) >= 1:
        score += 2

    # 4. Title не пустой и не совпадает с доменом
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True).lower() if title_tag else ""
    if title and domain_root not in title and len(title) > 5:
        score += 2

    return score >= 5


# =======================
# CLASSIFICATION
# =======================

def _fetch(url: str, session: requests.Session):
    """Один HTTP-запрос. Возвращает Response, 'ssl_error' или None."""
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        r.encoding = r.apparent_encoding
        return r
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
    root_domain = get_root_domain(domain)

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for scheme in ("https://", "http://"):
            url = scheme + domain
            result = _fetch(url, session)

            if result is None:
                continue

            if result == "ssl_error":
                return raw_url, "not_working"

            r: requests.Response = result

            # — Редирект на другой домен —
            final_domain = get_root_domain(normalize_url(r.url))
            if final_domain != root_domain:
                return raw_url, "not_working"

            # — Защита: только 401 и 429 —
            if r.status_code in PROTECTED_CODES:
                return raw_url, "protected"

            # — Не работает: мёртвые коды —
            if r.status_code in DEAD_CODES:
                return raw_url, "not_working"

            if r.status_code != 200:
                return raw_url, "not_working"

            # — Доп. фильтр: явные фразы парковки —
            if detect_parking(r.text):
                return raw_url, "not_working"

            # — Скоринг: живой сайт или заглушка хостинга —
            if is_alive(r.text, domain):
                if is_excluded_content(r.text):
                    return raw_url, "not_working"
                return raw_url, "working"
            else:
                return raw_url, "not_working"

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
    return list(dict.fromkeys(u.strip() for u in urls if u.strip()))


# =======================
# SAVE
# =======================

def save_results(results: dict[str, list[str]]):

    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')
    folder = 'results'

    os.makedirs(folder, exist_ok=True)

    output_file = f"{folder}/result_{cur_time}.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for status, urls in results.items():
            pd.DataFrame({"url": urls}).to_excel(
                writer,
                sheet_name=status,
                index=False
            )

    print(f"\nDone → {output_file}")


# =======================
# MAIN
# =======================

def main():
    folder = 'data'
    print("Loading URLs...")
    urls = load_urls_from_excels(folder)
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

    execution_time = datetime.now() - start_time
    print(f'Executed time: {execution_time}')


if __name__ == "__main__":
    main()
