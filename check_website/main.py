import os
import glob
import requests
import pandas as pd
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, SSLError, Timeout, ConnectionError

start_time = datetime.now()

# =======================
# CONFIG
# =======================

FOLDER = "data"
OUTPUT_FILE = "results/result.xlsx"
TIMEOUT = 8
MAX_WORKERS = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PARKING_PHRASES = [
    "domain for sale", "buy this domain", "coming soon",
    "under construction", "domain is parked",
    "домен продается", "домен продаётся",
    "премиум-домен", "купить домен",
    "домен на продажу"
]

BAD_REDIRECTS = ["login", "signin", "auth", "account", "register"]

PARKING_STRONG = [
    "домен продается",
    "домен продаётся",
    "магазин доменов",
    "премиум-домен",
    "идеальный домен",
    "дата выставления на продажу",
    "яндекс тиц",
    "pagerank",
    "reg.ru",
    "nic.ru",
    "купить домен",
    "продление домена",
    "выставлен на продажу"
]

# =======================
# HELPERS
# =======================

def is_trash_url(url: str) -> bool:
    return str(url).strip().lower() in ["", "nan", "none", "-", "null"]


def clean_domain(url: str) -> str:
    url = str(url).strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    domain = url.split("//")[-1].split("/")[0]

    if domain.startswith("www."):
        domain = domain[4:]

    return domain.lower()


def normalize_url(url: str) -> str:
    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def try_connect(url: str, session: requests.Session):
    try:
        return session.get(url, timeout=TIMEOUT, allow_redirects=True)
    except SSLError:
        if url.startswith("https://"):
            try:
                return session.get(url.replace("https://", "http://"), timeout=TIMEOUT)
            except:
                return None
    except (Timeout, ConnectionError, RequestException):
        return None


def extract_text(html: str):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split()).lower()

    return text, soup, title.lower()


def detect_parking(text: str, title: str) -> bool:
    for phrase in PARKING_PHRASES:
        if phrase in text or phrase in title:
            return True
    return False


def is_domain_parking(text: str) -> bool:
    text = text.lower()
    hits = sum(1 for p in PARKING_STRONG if p in text)
    return hits >= 2


def content_score(text: str, soup: BeautifulSoup) -> int:
    score = 0
    words = len(text.split())

    if words > 1000:
        score += 3
    elif words > 500:
        score += 2
    elif words > 100:
        score += 1
    elif words < 20:
        score -= 2

    if soup.find("article"):
        score += 2
    if soup.find("main"):
        score += 2
    if len(soup.find_all("p")) > 5:
        score += 1
    if soup.find("h1"):
        score += 1

    if len(soup.find_all("a")) > 10:
        score += 1

    unique_ratio = len(set(text.split())) / max(words, 1)
    if unique_ratio < 0.3 and words > 100:
        score -= 5

    return score


# =======================
# CLASSIFICATION
# =======================

def classify_website(url: str, session: requests.Session):

    if is_trash_url(url):
        return url, "not_working"

    original_url = url
    url = normalize_url(url)

    r = try_connect(url, session)

    domain = clean_domain(original_url)

    if r is None:
        return domain, "not_working"

    status = r.status_code

    # PROTECTED
    if status in (401, 403, 429):
        return domain, "protected"

    if any(x in r.url.lower() for x in BAD_REDIRECTS):
        return domain, "protected"

    if status >= 400:
        return domain, "not_working"

    text, soup, title = extract_text(r.text)
    word_count = len(text.split())

    # 🔥 HARD FILTER (ВАЖНО ПЕРВЫМ)
    if is_domain_parking(text):
        return domain, "not_working"

    if detect_parking(text, title):
        return domain, "not_working"

    if len(r.content) < 300 and word_count < 30:
        return domain, "not_working"

    score = content_score(text, soup)

    if score >= 4:
        return domain, "working"

    return domain, "not_working"


# =======================
# LOAD
# =======================

def load_urls(folder: str):
    files = glob.glob(os.path.join(folder, "*.xls*"))

    urls = []

    for file in files:
        df = pd.read_excel(file, header=None)
        urls.extend(df.iloc[:, 0].dropna().astype(str).tolist())

    return list(dict.fromkeys(urls))


# =======================
# SAVE
# =======================

def save_results(results):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        for k, v in results.items():
            if v:
                pd.DataFrame({"domain": v}).to_excel(writer, sheet_name=k, index=False)


# =======================
# MAIN
# =======================

def main():
    urls = load_urls(FOLDER)

    results = {
        "working": [],
        "not_working": [],
        "protected": []
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(classify_website, url, session) for url in urls]

        for i, future in enumerate(as_completed(futures), 1):
            domain, status = future.result()
            results[status].append(domain)

            if i % 30 == 0:
                print(f"Processed: {i}/{len(urls)} urls")

    save_results(results)

    print("\nDone:", {k: len(v) for k, v in results.items()})

    execution_time = datetime.now() - start_time
    print(f"Total time: {execution_time}")


if __name__ == "__main__":
    main()
