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
    "this domain is for sale",
    "прилинкуйте домен",
    "домен никуда не направлен"
]


# =======================
# HELPERS
# =======================

def normalize_url(url: str) -> str:
    if not url.startswith("http"):
        return "http://" + url
    return url


def detect_parking(text: str) -> bool:
    text = text.lower()
    return any(p in text for p in PARKING_PHRASES)


def extract_text(html: str) -> str:
    """
    Минимальная очистка HTML → текст
    """
    html = html.lower()

    # грубое удаление шумных блоков
    for tag in ["script", "style", "noscript"]:
        html = html.replace(f"<{tag}", " <")

    return html


# =======================
# CLASSIFICATION
# =======================

def classify_website(url: str, session: requests.Session) -> str:
    url = normalize_url(url)

    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)

        # =======================
        # PROTECTED
        # =======================
        if r.status_code == 403:
            return "protected"

        if r.status_code in (401, 429):
            return "protected"

        if "cloudflare" in r.text.lower() and "captcha" in r.text.lower():
            return "protected"

        # =======================
        # NOT WORKING
        # =======================
        if r.status_code in (404, 410):
            return "not_working"

        if r.status_code != 200:
            return "not_working"

        html = extract_text(r.text)

        if detect_parking(html):
            return "not_working"

        # слишком пустая страница
        if len(html) < 300:
            return "not_working"

        # =======================
        # WORKING
        # =======================
        return "working"

    except SSLError:
        return "protected"

    except RequestException:
        return "not_working"


# =======================
# LOAD DATA
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
        "protected": []
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