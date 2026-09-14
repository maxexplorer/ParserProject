import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook

try:
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    from undetected_chromedriver import Chrome as UndetectedChrome
    from undetected_chromedriver import ChromeOptions
except ImportError:
    By = None
    TimeoutException = None
    UndetectedChrome = None
    ChromeOptions = None


START_URL = (
    "https://www.avito.ru/brands/i163368046/all?"
    "gdlkerfdnwq=101&shopId=325829&page_from=from_item_card&iid=8266865175&"
    "sellerId=68e411e472dd465f45c2d88abf65c4ad&q=%D1%81%D1%814"
)

BASE_URL = "https://www.avito.ru"
PROFILE_ITEMS_URL = f"{BASE_URL}/web/1/profile/items"
RESULT_DIR = Path(__file__).resolve().parent / "results"
URLS_FILE = RESULT_DIR / "product_urls.txt"
BROWSER_DELAY_SECONDS = 2
PAGE_LOAD_TIMEOUT = 45
DEFAULT_MAX_PAGES = 200


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = re.sub(r"\s+", " ", str(value))
    return text.strip() or None


def get_seller_id(url: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    seller_id = query_params.get("sellerId", [None])[0]

    if not seller_id:
        raise ValueError("Не удалось найти sellerId в ссылке Avito")

    return seller_id


def normalize_image_url(url: str | None) -> str | None:
    if not url:
        return None

    url = unescape(str(url))
    url = url.replace("\\u002F", "/").replace("\\/", "/")

    if url.startswith("//"):
        url = f"https:{url}"
    elif url.startswith("/"):
        url = urljoin(BASE_URL, url)

    if not url.startswith(("http://", "https://")):
        return None

    if not any(host_part in url for host_part in ("img.avito.st", "avito.st/image")):
        return None

    url = url.rstrip('",;)]}')
    parsed_url = urlparse(url)
    return parsed_url._replace(query="", fragment="").geturl()


def get_image_score(url: str) -> int:
    sizes = re.findall(r"(\d{2,5})[xX](\d{2,5})", url)
    if not sizes:
        return 0

    return max(int(width) * int(height) for width, height in sizes)


def image_identity(url: str) -> str:
    parsed_url = urlparse(url)
    path = parsed_url.path

    if "/image/1/1." in path:
        return path.split("/image/1/1.", 1)[-1].split(".", 1)[0]

    netloc = re.sub(r"^\d+\.", "", parsed_url.netloc)
    return f"{netloc}{path}"


def sort_and_dedupe_images(images: list[str]) -> list[str]:
    best_by_identity: dict[str, tuple[int, int, str]] = {}

    for index, image_url in enumerate(images):
        normalized_url = normalize_image_url(image_url)
        if not normalized_url:
            continue

        identity = image_identity(normalized_url)
        score = get_image_score(normalized_url)
        current = best_by_identity.get(identity)

        if current is None or score > current[0]:
            best_by_identity[identity] = (score, index, normalized_url)

    return [
        image_url
        for _, _, image_url in sorted(
            best_by_identity.values(),
            key=lambda item: (-item[0], item[1]) if item[0] else (0, item[1]),
        )
    ]


def add_image(images: list[str], image_url: str | None) -> None:
    normalized_url = normalize_image_url(image_url)

    if normalized_url and normalized_url not in images:
        images.append(normalized_url)


def find_image_urls_in_object(data: Any) -> list[str]:
    images: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                key_lower = str(key).lower()
                if isinstance(item, str) and any(part in key_lower for part in ("image", "img", "photo", "url")):
                    add_image(images, item)
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            add_image(images, value)

    walk(data)
    return sort_and_dedupe_images(images)


def extract_json_ld(soup: BeautifulSoup) -> list[dict[str, Any]]:
    json_ld_objects: list[dict[str, Any]] = []

    for script in soup.select('script[type="application/ld+json"]'):
        script_text = script.string or script.get_text(strip=True)
        if not script_text:
            continue

        try:
            loaded_data = json.loads(script_text)
        except json.JSONDecodeError:
            continue

        if isinstance(loaded_data, list):
            json_ld_objects.extend(item for item in loaded_data if isinstance(item, dict))
        elif isinstance(loaded_data, dict):
            json_ld_objects.append(loaded_data)

    return json_ld_objects


def parse_price_from_json_ld(data: dict[str, Any]) -> int | str | None:
    offers = data.get("offers") or {}

    if isinstance(offers, list):
        offers = offers[0] if offers else {}

    if isinstance(offers, dict):
        return offers.get("price") or offers.get("lowPrice")

    return None


def extract_images_from_html(html: str, soup: BeautifulSoup) -> list[str]:
    images: list[str] = []

    for data in extract_json_ld(soup):
        image_data = data.get("image")
        if isinstance(image_data, list):
            for image_url in image_data:
                add_image(images, image_url)
        else:
            add_image(images, image_data)

    for meta_selector in (
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        'meta[itemprop="image"]',
    ):
        for meta in soup.select(meta_selector):
            add_image(images, meta.get("content"))

    return sort_and_dedupe_images(images)


def parse_product_page(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    title = parse_title_from_html(soup)
    data: dict[str, Any] = {
        "title": title,
        "price": None,
        "images": [],
    }

    for json_ld in extract_json_ld(soup):
        if not data["title"]:
            data["title"] = clean_text(json_ld.get("name"))
        if not data["price"]:
            data["price"] = parse_price_from_json_ld(json_ld)

    if not data["title"]:
        h1 = soup.select_one('h1[itemprop="name"], h1')
        data["title"] = clean_text(h1.get_text(" ", strip=True) if h1 else None)

    if not data["title"]:
        meta_title = soup.select_one('meta[property="og:title"], meta[name="twitter:title"]')
        data["title"] = clean_text(meta_title.get("content") if meta_title else None)

    if not data["title"] and soup.title:
        data["title"] = clean_text(soup.title.get_text(" ", strip=True).split("|")[0])

    if not data["price"]:
        price_meta = soup.select_one('meta[itemprop="price"]')
        data["price"] = price_meta.get("content") if price_meta else None

    if not data["price"]:
        price_node = soup.select_one('[data-marker="item-view/item-price"], [itemprop="price"]')
        data["price"] = clean_text(price_node.get_text(" ", strip=True) if price_node else None)

    carousel_images = extract_carousel_images(soup, data.get("title"))
    data["images"] = carousel_images or extract_images_from_html(html, soup)

    return data


def is_valid_product_data(data: dict[str, Any]) -> bool:
    title = clean_text(data.get("title")) or ""
    blocked_patterns = (
        "доступ ограничен",
        "проблема с ip",
        "captcha",
        "капча",
        "проверка",
    )

    if any(pattern in title.lower() for pattern in blocked_patterns):
        return False

    return bool(data.get("title") or data.get("price"))


def parse_title_from_html(soup: BeautifulSoup) -> str | None:
    h1 = soup.select_one('h1[itemprop="name"], h1')
    title = clean_text(h1.get_text(" ", strip=True) if h1 else None)

    if title:
        return title

    meta_title = soup.select_one('meta[property="og:title"], meta[name="twitter:title"]')
    title = clean_text(meta_title.get("content") if meta_title else None)

    if title:
        return title

    if soup.title:
        return clean_text(soup.title.get_text(" ", strip=True).split("|")[0])

    return None


def extract_carousel_images(soup: BeautifulSoup, title: str | None) -> list[str]:
    if not title:
        return []

    title_words = set(re.findall(r"[a-zA-Zа-яА-Я0-9]+", title.lower()))
    images: list[str] = []

    for image in soup.select('li[role="option"] img[src], img[draggable="false"][src]'):
        alt = clean_text(image.get("alt"))
        src = image.get("src")

        if not alt or not src:
            continue

        alt_words = set(re.findall(r"[a-zA-Zа-яА-Я0-9]+", alt.lower()))
        if title_words and len(title_words & alt_words) < min(2, len(title_words)):
            continue

        add_image(images, src)

    return sort_and_dedupe_images(images)


def extract_carousel_images(soup: BeautifulSoup, title: str | None) -> list[str]:
    if not title:
        return []

    title_lower = title.lower()
    title_words = set(re.findall(r"\w+", title_lower, flags=re.UNICODE))
    images: list[str] = []

    for image in soup.select('li[role="option"] img[src], img[draggable="false"][src], img[alt][src]'):
        alt = clean_text(image.get("alt"))
        src = image.get("src")

        if not alt or not src:
            continue

        alt_lower = alt.lower()
        alt_words = set(re.findall(r"\w+", alt_lower, flags=re.UNICODE))
        if title_lower not in alt_lower and title_words and len(title_words & alt_words) < min(2, len(title_words)):
            continue

        add_image(images, src)

    return sort_and_dedupe_images(images)


def collect_carousel_images_from_browser(driver: Any, title: str | None) -> list[str]:
    if not title:
        return []

    gallery_images: list[str] = []
    for image_url in collect_gallery_images_from_browser(driver):
        add_image(gallery_images, image_url)

    large_images: list[str] = []
    thumbnails = driver.find_elements(
        By.CSS_SELECTOR,
        'ul[role="listbox"][aria-orientation="horizontal"] li[role="option"], '
        'ul[role="listbox"][aria-orientation="horizontal"] button',
    )

    if thumbnails:
        for thumbnail in thumbnails:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", thumbnail)
                driver.execute_script("arguments[0].click();", thumbnail)
                time.sleep(0.35)

                for image_url in collect_large_images_from_browser(driver, title):
                    add_image(large_images, image_url)
            except Exception:
                continue

        if large_images and len(large_images) >= max(1, len(gallery_images) // 2):
            return sort_and_dedupe_images(large_images)

    for image_url in collect_large_images_from_browser(driver, title):
        add_image(large_images, image_url)

    if large_images:
        return sort_and_dedupe_images(large_images)

    return sort_and_dedupe_images(gallery_images)


def collect_gallery_images_from_browser(driver: Any) -> list[str]:
    script = """
        const urls = [];

        document
            .querySelectorAll('ul[role="listbox"][aria-orientation="horizontal"] img[src]')
            .forEach(img => {
                const src = img.currentSrc || img.src || img.getAttribute("src");
                if (src && src.includes("img.avito.st")) {
                    urls.push(src);
                }
            });

        return Array.from(new Set(urls));
    """

    try:
        return driver.execute_script(script) or []
    except Exception as ex:
        print(f"Не удалось собрать фото из галереи миниатюр: {ex}")

    return []


def collect_large_images_from_browser(driver: Any, title: str | None) -> list[str]:
    script = """
        const title = arguments[0].toLowerCase();
        const titleWords = new Set((title.match(/[\\p{L}\\p{N}_]+/gu) || []));
        const urls = [];

        function isProductImage(img) {
            const alt = (img.getAttribute("alt") || "").trim().toLowerCase();
            const src = img.currentSrc || img.src || img.getAttribute("src") || img.getAttribute("srcset") || "";
            const rect = img.getBoundingClientRect();

            if (!src || !src.includes("img.avito.st")) {
                return false;
            }

            if (img.closest('ul[role="listbox"][aria-orientation="horizontal"]')) {
                return false;
            }

            if (rect.width < 180 || rect.height < 180) {
                return false;
            }

            if (alt.includes(title)) {
                return true;
            }

            if (!alt) {
                return true;
            }

            const altWords = new Set((alt.match(/[\\p{L}\\p{N}_]+/gu) || []));
            let common = 0;

            for (const word of titleWords) {
                if (altWords.has(word)) {
                    common += 1;
                }
            }

            return common >= Math.min(2, titleWords.size);
        }

        document
            .querySelectorAll('img[src], picture source[srcset]')
            .forEach(img => {
                if (isProductImage(img)) {
                    const src = img.currentSrc || img.src || img.getAttribute("src") || img.getAttribute("srcset");
                    urls.push(src.split(",")[0].trim().split(" ")[0]);
                }
            });

        return Array.from(new Set(urls));
    """

    try:
        return driver.execute_script(script, title) or []
    except Exception as ex:
        print(f"Не удалось собрать большое фото из DOM: {ex}")

    return []


def normalize_product_url(url: str | None) -> str | None:
    if not url:
        return None

    url = unescape(str(url)).replace("\\u002F", "/").replace("\\/", "/")
    url = url.rstrip('",;)]}')

    if url.startswith("//"):
        url = f"https:{url}"
    elif url.startswith("/"):
        url = urljoin(BASE_URL, url)

    parsed_url = urlparse(url)
    if not parsed_url.netloc.endswith("avito.ru"):
        return None

    if "/brands/" in parsed_url.path:
        return None

    if not re.search(r"_\d{6,}$", parsed_url.path):
        return None

    return parsed_url._replace(query="", fragment="").geturl()


def make_listing_page_url(seller_url: str, page: int) -> str:
    parsed_url = urlparse(seller_url)
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    query_params["p"] = [str(page)]

    query = urlencode(query_params, doseq=True)
    return parsed_url._replace(query=query).geturl()


def extract_product_urls_from_html(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    product_urls: list[str] = []

    def add_product_url(raw_url: str | None) -> None:
        product_url = normalize_product_url(raw_url)
        if product_url and product_url not in product_urls:
            product_urls.append(product_url)

    for anchor in soup.select("a[href]"):
        add_product_url(anchor.get("href"))

    decoded_html = unescape(html).replace("\\u002F", "/").replace("\\/", "/")
    url_patterns = (
        r"https?://www\.avito\.ru/[^\s\"'<>\\]+_\d{6,}",
        r"/[a-zA-Zа-яА-Я0-9_./%+-]+_\d{6,}",
    )

    for pattern in url_patterns:
        for raw_url in re.findall(pattern, decoded_html, flags=re.IGNORECASE):
            add_product_url(raw_url)

    return product_urls


def get_chrome_major_version() -> int | None:
    chrome_dirs = (
        r"C:\Program Files\Google\Chrome\Application",
        r"C:\Program Files (x86)\Google\Chrome\Application",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application"),
    )

    for chrome_dir in chrome_dirs:
        if not os.path.isdir(chrome_dir):
            continue

        for entry in os.listdir(chrome_dir):
            version_match = re.fullmatch(r"(\d+)\.\d+\.\d+\.\d+", entry)
            if version_match:
                return int(version_match.group(1))

    commands = (
        [r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--version"],
        [r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "--version"],
        ["google-chrome", "--version"],
        ["chrome", "--version"],
    )

    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            continue

        output = result.stdout or result.stderr or ""
        version_match = re.search(r"(?:Google Chrome|Chrome|Chromium)\s+(\d+)\.", output, flags=re.IGNORECASE)
        if version_match:
            return int(version_match.group(1))

    return None


def init_browser(headless: bool = False) -> Any:
    if UndetectedChrome is None or ChromeOptions is None:
        raise RuntimeError("Не установлен undetected_chromedriver")

    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

    if headless:
        options.add_argument("--headless=new")

    driver_kwargs = {"options": options}
    version_main = get_chrome_major_version()

    if version_main:
        driver_kwargs["version_main"] = version_main

    driver = UndetectedChrome(**driver_kwargs)
    driver.implicitly_wait(5)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.set_script_timeout(PAGE_LOAD_TIMEOUT)

    if not headless:
        driver.maximize_window()

    return driver


def safe_get(driver: Any, url: str) -> None:
    try:
        driver.get(url)
    except Exception as ex:
        if TimeoutException is not None and isinstance(ex, TimeoutException):
            print(f"Страница долго грузится, останавливаю загрузку: {url}")
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass
            return

        raise


def wait_if_captcha(driver: Any) -> None:
    page_text = f"{driver.title or ''} {driver.page_source[:8000]}"

    if re.search(r"captcha|капч|доступ ограничен|подтвердите|проверка", page_text, flags=re.IGNORECASE):
        print("Avito показывает проверку/капчу. Пройдите её в открытом окне браузера.")
        try:
            input("После прохождения капчи нажмите Enter здесь, чтобы продолжить...")
        except EOFError:
            print("Консоль не принимает Enter. Жду 60 сек и пробую продолжить...")
            time.sleep(60)
        time.sleep(BROWSER_DELAY_SECONDS)


def parse_price_from_item(item: dict[str, Any]) -> int | str | None:
    price_detailed = item.get("priceDetailed") or {}

    if price_detailed.get("value") is not None:
        return price_detailed.get("value")

    if price_detailed.get("normalizedPrice"):
        return price_detailed.get("normalizedPrice")

    price = item.get("price")
    if isinstance(price, dict):
        return price.get("value") or price.get("text") or price.get("string")

    return price


def parse_item_from_listing(item: dict[str, Any]) -> dict[str, Any]:
    relative_url = item.get("urlPath") or item.get("url")
    product_url = urljoin(BASE_URL, relative_url) if relative_url else None

    return {
        "title": clean_text(item.get("title")),
        "price": parse_price_from_item(item),
        "url": product_url,
        "images": find_image_urls_in_object(item),
    }


def browser_fetch_json(driver: Any, url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    script = """
        const callback = arguments[arguments.length - 1];
        const url = new URL(arguments[0]);
        const params = arguments[1];

        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.set(key, value);
        });

        fetch(url.toString(), {
            method: "GET",
            credentials: "include",
            headers: {
                "accept": "application/json",
                "x-requested-with": "XMLHttpRequest"
            }
        })
            .then(async response => {
                const text = await response.text();
                callback({
                    ok: response.ok,
                    status: response.status,
                    text
                });
            })
            .catch(error => callback({
                ok: false,
                status: 0,
                text: String(error)
            }));
    """
    result = driver.execute_async_script(script, url, params)

    if not result or not result.get("ok"):
        print(f"Browser fetch Avito API не удался, статус {result.get('status') if result else 'unknown'}")
        return None

    try:
        return json.loads(result.get("text") or "{}")
    except json.JSONDecodeError:
        return None


def get_profile_items_params(seller_url: str, page: int, limit: int) -> dict[str, Any]:
    query_params = parse_qs(urlparse(seller_url).query)
    params: dict[str, Any] = {
        "p": page,
        "sellerId": get_seller_id(seller_url),
        "itemsOnPage": limit,
        "limit": limit,
    }

    if query_params.get("q"):
        params["q"] = query_params["q"][-1]

    if query_params.get("shopId"):
        params["shopId"] = query_params["shopId"][-1]

    return params


def collect_listing_items_from_browser_api(
    driver: Any,
    seller_url: str,
    max_items: int | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
    limit: int = 100,
) -> list[dict[str, Any]]:
    listing_items: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    safe_get(driver, seller_url)
    time.sleep(BROWSER_DELAY_SECONDS)
    wait_if_captcha(driver)

    for page in range(1, max_pages + 1):
        json_data = browser_fetch_json(
            driver=driver,
            url=PROFILE_ITEMS_URL,
            params=get_profile_items_params(seller_url=seller_url, page=page, limit=limit),
        )

        if not json_data:
            break

        total = json_data.get("foundCount") or json_data.get("totalCount")
        items = json_data.get("catalog", {}).get("items", []) or []
        new_items = []

        for item in items:
            parsed_item = parse_item_from_listing(item)
            product_url = parsed_item.get("url")

            if product_url and product_url not in seen_urls:
                seen_urls.add(product_url)
                new_items.append(parsed_item)

        listing_items.extend(new_items)
        print(
            f"API в браузере: страница {page}, новых {len(new_items)}, "
            f"всего {len(listing_items)} из {total or '?'}"
        )

        if max_items and len(listing_items) >= max_items:
            return listing_items[:max_items]

        if not items or not new_items:
            break

    return listing_items


def save_product_urls(product_urls: list[str], file_path: Path = URLS_FILE) -> str:
    os.makedirs(file_path.parent, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        for product_url in product_urls:
            file.write(f"{product_url}\n")

    return str(file_path)


def read_product_urls(file_path: Path = URLS_FILE) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"Файл со ссылками не найден: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return list(dict.fromkeys(line.strip() for line in file if line.strip()))


def collect_product_urls_from_browser(
    driver: Any,
    seller_url: str,
    max_items: int | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> list[str]:
    product_urls: list[str] = []
    empty_pages = 0

    for page in range(1, max_pages + 1):
        page_url = make_listing_page_url(seller_url, page)
        safe_get(driver, page_url)
        time.sleep(BROWSER_DELAY_SECONDS)
        wait_if_captcha(driver)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        page_product_urls = extract_product_urls_from_html(driver.page_source)
        new_urls = []

        for product_url in page_product_urls:
            if product_url and product_url not in product_urls:
                product_urls.append(product_url)
                new_urls.append(product_url)

        print(
            f"Страница выдачи {page}: найдено новых ссылок {len(new_urls)}, "
            f"всего {len(product_urls)}"
        )

        if max_items and len(product_urls) >= max_items:
            return product_urls[:max_items]

        if not new_urls:
            empty_pages += 1
        else:
            empty_pages = 0

        if empty_pages >= 2:
            break

    return product_urls


def collect_all_product_urls_with_browser(
    driver: Any,
    seller_url: str,
    max_items: int | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> list[str]:
    listing_items = collect_listing_items_from_browser_api(
        driver=driver,
        seller_url=seller_url,
        max_items=max_items,
        max_pages=max_pages,
    )

    product_urls = [
        listing_item["url"]
        for listing_item in listing_items
        if listing_item.get("url")
    ]

    if product_urls:
        return list(dict.fromkeys(product_urls))

    return collect_product_urls_from_browser(
        driver=driver,
        seller_url=seller_url,
        max_items=max_items,
        max_pages=max_pages,
    )


def parse_products_from_urls(
    driver: Any,
    product_urls: list[str],
    batch_size: int = 20,
    start_from: int = 1,
    stop_at: int | None = None,
) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    total_saved = 0
    start_index = max(1, start_from)
    end_index = min(stop_at or len(product_urls), len(product_urls))
    product_urls = product_urls[start_index - 1:end_index]

    for index, product_url in enumerate(product_urls, start_index):
        try:
            safe_get(driver, product_url)
            time.sleep(BROWSER_DELAY_SECONDS)
            wait_if_captcha(driver)

            page_data = parse_product_page(driver.page_source)
            carousel_images = collect_carousel_images_from_browser(driver, page_data.get("title"))
            images = carousel_images or page_data.get("images", [])

            product_data = {
                "title": page_data.get("title"),
                "price": page_data.get("price"),
                "url": product_url,
                "images": sort_and_dedupe_images(images),
            }

            if not is_valid_product_data(product_data):
                raise ValueError("страница объявления не распознана: нет заголовка и цены")

        except Exception as ex:
            print(f"Не удалось обработать карточку в браузере {product_url}: {ex}")
            continue

        products.append(product_data)
        print(
            f"Браузер: обработано {index}/{end_index}: "
            f"{product_data.get('title') or 'без заголовка'} "
            f"({len(product_data.get('images', []))} фото)"
        )

        if batch_size > 0 and len(products) >= batch_size:
            file_path = save_excel(products)
            total_saved += len(products)
            print(f"Промежуточно сохранено {total_saved} объявлений: {file_path}")
            products.clear()

    if products:
        file_path = save_excel(products)
        total_saved += len(products)
        print(f"Сохранён остаток. Всего сохранено {total_saved} объявлений: {file_path}")
        products.clear()

    return products


def build_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for product in products:
        row = {
            "Заголовок": product.get("title"),
            "Цена": product.get("price"),
            "Ссылка": product.get("url"),
            "Фото": "|".join(product.get("images", [])),
        }

        rows.append(row)

    return rows


def save_excel(products: list[dict[str, Any]]) -> str:
    if not products:
        return ""

    os.makedirs(RESULT_DIR, exist_ok=True)

    current_date = datetime.now().strftime("%d%m%Y")
    file_path = RESULT_DIR / f"result_data_{current_date}.xlsx"
    rows = build_rows(products)

    if not file_path.exists():
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "data"
        worksheet.append(list(rows[0].keys()))
    else:
        workbook = load_workbook(file_path)
        worksheet = workbook["data"] if "data" in workbook.sheetnames else workbook.active

    for row in rows:
        worksheet.append(list(row.values()))

    workbook.save(file_path)

    print(f"Сохранено {worksheet.max_row - 1} записей в {file_path}")
    return str(file_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Парсер объявлений Avito в Excel")
    parser.add_argument("--url", default=START_URL, help="Ссылка на магазин/профиль Avito")
    parser.add_argument("--stage", choices=("all", "links", "data"), default="data", help="Этап: all, links или data")
    parser.add_argument("--urls-file", default=str(URLS_FILE), help="Файл для сохранения/чтения ссылок")
    parser.add_argument("--max-items", type=int, default=None, help="Ограничение количества объявлений для теста")
    parser.add_argument("--start-from", type=int, default=1, help="Начать обработку data-этапа с N-й ссылки")
    parser.add_argument("--stop-at", type=int, default=400, help="Остановить обработку data-этапа на N-й ссылке")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="Максимум страниц выдачи для сбора ссылок")
    parser.add_argument("--batch-size", type=int, default=20, help="Сохранять Excel каждые N объявлений, 0 отключает")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    encoded_url = quote(args.url, safe=":/?&=%")
    urls_file = Path(args.urls_file)

    print("Старт сбора данных Avito")
    driver = init_browser(headless=False)

    try:
        if args.stage in ("all", "links"):
            product_urls = collect_all_product_urls_with_browser(
                driver=driver,
                seller_url=encoded_url,
                max_items=args.max_items,
                max_pages=args.max_pages,
            )
            urls_path = save_product_urls(product_urls, urls_file)
            print(f"Ссылки сохранены: {urls_path}. Всего ссылок: {len(product_urls)}")

            if args.stage == "links":
                return

        product_urls = read_product_urls(urls_file)

        if args.max_items:
            product_urls = product_urls[:args.max_items]

        products = parse_products_from_urls(
            driver=driver,
            product_urls=product_urls,
            batch_size=args.batch_size,
            start_from=args.start_from,
            stop_at=args.stop_at,
        )

    finally:
        driver.quit()

    if not products:
        print("Данные не собраны, пустой Excel не сохраняю.")
        return

    file_path = save_excel(products)

    print(f"Готово. Собрано объявлений: {len(products)}")
    print(f"Файл сохранён: {file_path}")


if __name__ == "__main__":
    main()
