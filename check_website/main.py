import os
import glob
import requests
import pandas as pd

from requests.exceptions import RequestException, SSLError


# =======================
# CONFIG
# =======================

FOLDER: str = "data"
OUTPUT_FILE: str = "result.xlsx"
TIMEOUT: int = 5

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
    "прилинкуйте домен",
    "домен никуда не направлен"
]


# =======================
# CORE LOGIC
# =======================

def normalize_url(url: str) -> str:
    if not url.startswith("http"):
        return "http://" + url
    return url


def detect_parking(html: str) -> bool:
    html = html.lower()
    return any(p in html for p in PARKING_PHRASES)


def content_score(html: str) -> int:
    """
    Оценивает "живость" сайта
    """
    score = 0

    html_lower = html.lower()

    # базовые признаки контента
    if "<h1" in html_lower:
        score += 2
    if "<p" in html_lower:
        score += 2
    if "<article" in html_lower:
        score += 3
    if len(html_lower) > 1500:
        score += 2

    # негатив
    if "javascript" in html_lower:
        score += 1  # SPA не плохо
    if detect_parking(html_lower):
        score -= 10

    return score


def classify_website(url: str, session: requests.Session) -> str:
    url = normalize_url(url)

    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)

        # --- HTTP level ---
        if r.status_code == 403:
            return "protected"

        if r.status_code in (404, 410):
            return "not_working"

        if r.status_code != 200:
            return "not_working"

        html = r.text

        # --- parking detection ---
        if detect_parking(html):
            return "not_working"

        # --- content scoring ---
        score = content_score(html)

        if score >= 4:
            return "working"
        elif score >= 1:
            return "uncertain"
        else:
            return "not_working"

    except SSLError:
        return "protected"

    except RequestException:
        return "not_working"


# =======================
# FILE LOADING
# =======================

def load_urls_from_excels(folder: str) -> list[str]:
    files = glob.glob(os.path.join(folder, "*.xls*"))

    urls = []

    for file in files:
        df = pd.read_excel(file, sheet_name=0, header=None)
        urls.extend(df.iloc[:, 0].dropna().tolist())

    return urls


# =======================
# SAVE
# =======================

def save_results(results: dict[str, list[str]]):
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for k, v in results.items():
            pd.DataFrame({"url": v}).to_excel(writer, sheet_name=k, index=False)


# =======================
# MAIN
# =======================

def main():
    print("Loading URLs...")
    urls = load_urls_from_excels(FOLDER)

    print(f"Total: {len(urls)}")

    results = {
        "working": [],
        "not_working": [],
        "protected": [],
        "uncertain": []
    }

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for i, url in enumerate(urls, 1):

            status = classify_website(url, session)
            results[status].append(url)

            if i % 50 == 0:
                print(f"{i}/{len(urls)} processed")

    save_results(results)

    print("Done")


if __name__ == "__main__":
    main()