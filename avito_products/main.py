import argparse
import json
import math
import os
import re
import time
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urljoin, urlparse

from bs4 import BeautifulSoup
from pandas import DataFrame, ExcelWriter
from requests import HTTPError, RequestException, Session


START_URL = (
    "https://www.avito.ru/brands/i163368046/all?"
    "gdlkerfdnwq=101&shopId=325829&page_from=from_item_card&iid=8266865175&"
    "sellerId=68e411e472dd465f45c2d88abf65c4ad&q=cc4s=profile_search_button&q=cc4"
)

BASE_URL = "https://www.avito.ru"
PROFILE_ITEMS_URL = f"{BASE_URL}/web/1/profile/items"
RESULT_DIR = Path(__file__).resolve().parent / "results"
REQUEST_TIMEOUT = 30
DELAY_SECONDS = 1.2


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


def make_headers(referer: str, accept: str = "application/json") -> dict[str, str]:
    return {
        "accept": accept,
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": referer,
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        "x-requested-with": "XMLHttpRequest",
    }


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

    return url.rstrip('",;)]}')


def get_image_score(url: str) -> int:
    sizes = re.findall(r"(\d{2,5})[xX](\d{2,5})", url)
    if not sizes:
        return 0

    return max(int(width) * int(height) for width, height in sizes)


def image_identity(url: str) -> str:
    parsed_url = urlparse(url)
    netloc = re.sub(r"^\d+\.", "", parsed_url.netloc)
    return f"{netloc}{parsed_url.path}"


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

    decoded_html = unescape(html).replace("\\u002F", "/").replace("\\/", "/")
    patterns = (
        r"https?://[0-9a-z.-]*img\.avito\.st/image/[^\s\"'<>\\]+",
        r"//[0-9a-z.-]*img\.avito\.st/image/[^\s\"'<>\\]+",
    )

    for pattern in patterns:
        for image_url in re.findall(pattern, decoded_html, flags=re.IGNORECASE):
            add_image(images, image_url)

    return sort_and_dedupe_images(images)


def parse_product_page(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    data: dict[str, Any] = {
        "title": None,
        "price": None,
        "images": extract_images_from_html(html, soup),
    }

    for json_ld in extract_json_ld(soup):
        if not data["title"]:
            data["title"] = clean_text(json_ld.get("name"))
        if not data["price"]:
            data["price"] = parse_price_from_json_ld(json_ld)

    if not data["title"]:
        h1 = soup.select_one('h1[itemprop="name"], h1')
        data["title"] = clean_text(h1.get_text(" ", strip=True) if h1 else None)

    if not data["price"]:
        price_meta = soup.select_one('meta[itemprop="price"]')
        data["price"] = price_meta.get("content") if price_meta else None

    if not data["price"]:
        price_node = soup.select_one('[data-marker="item-view/item-price"], [itemprop="price"]')
        data["price"] = clean_text(price_node.get_text(" ", strip=True) if price_node else None)

    return data


def fetch_listing_page(session: Session, seller_url: str, page: int, limit: int) -> dict[str, Any]:
    seller_id = get_seller_id(seller_url)
    headers = make_headers(seller_url)
    params = {
        "p": page,
        "sellerId": seller_id,
        "itemsOnPage": limit,
        "limit": limit,
    }

    response = session.get(PROFILE_ITEMS_URL, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_listing_items(
    session: Session,
    seller_url: str,
    limit: int = 100,
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    first_page = fetch_listing_page(session=session, seller_url=seller_url, page=1, limit=limit)
    total = first_page.get("foundCount") or first_page.get("totalCount") or 0
    pages = max(1, math.ceil(total / limit)) if total else 1
    all_items = first_page.get("catalog", {}).get("items", []) or []

    print(f"Найдено объявлений: {total or len(all_items)}. Страниц: {pages}")

    if max_items and len(all_items) >= max_items:
        return all_items[:max_items]

    for page in range(2, pages + 1):
        time.sleep(DELAY_SECONDS)
        try:
            page_data = fetch_listing_page(session=session, seller_url=seller_url, page=page, limit=limit)
        except HTTPError as ex:
            status_code = ex.response.status_code if ex.response is not None else None
            print(f"Страница списка {page} недоступна, статус {status_code}. Сохраняю уже собранные данные.")
            break

        items = page_data.get("catalog", {}).get("items", []) or []
        all_items.extend(items)
        print(f"Список объявлений: страница {page}/{pages}, собрано {len(all_items)}")

        if max_items and len(all_items) >= max_items:
            return all_items[:max_items]

    return all_items


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


def get_product_data(session: Session, product_url: str, fallback_data: dict[str, Any]) -> dict[str, Any]:
    headers = make_headers(product_url, accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

    response = session.get(product_url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    page_data = parse_product_page(response.text)

    images = []
    for image_url in page_data.get("images", []):
        add_image(images, image_url)
    for image_url in fallback_data.get("images", []):
        add_image(images, image_url)

    return {
        "title": page_data.get("title") or fallback_data.get("title"),
        "price": page_data.get("price") or fallback_data.get("price"),
        "url": product_url,
        "images": sort_and_dedupe_images(images),
    }


def collect_products(seller_url: str, limit: int = 100, max_items: int | None = None) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []

    with Session() as session:
        listing_items = get_listing_items(
            session=session,
            seller_url=seller_url,
            limit=limit,
            max_items=max_items,
        )

        for index, item in enumerate(listing_items, 1):
            fallback_data = parse_item_from_listing(item)
            product_url = fallback_data.get("url")

            if not product_url:
                continue

            try:
                time.sleep(DELAY_SECONDS)
                product_data = get_product_data(
                    session=session,
                    product_url=product_url,
                    fallback_data=fallback_data,
                )
            except Exception as ex:
                print(f"Не удалось открыть карточку {product_url}: {ex}")
                product_data = fallback_data

            products.append(product_data)
            print(
                f"Обработано {index}/{len(listing_items)}: "
                f"{product_data.get('title') or 'без заголовка'} "
                f"({len(product_data.get('images', []))} фото)"
            )

    return products


def collect_products_auto(
    seller_url: str,
    limit: int = 100,
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    try:
        return collect_products(seller_url=seller_url, limit=limit, max_items=max_items)
    except HTTPError as ex:
        status_code = ex.response.status_code if ex.response is not None else None
        print(f"API Avito недоступен, статус {status_code}.")
        if status_code == 429:
            print("Avito ограничил частоту запросов. Попробуйте позже, уменьшите --limit или добавьте прокси.")
    except RequestException as ex:
        print(f"Ошибка HTTP-запроса: {ex}")

    return []


def build_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for index, product in enumerate(products, 1):
        row = {
            "№": index,
            "Заголовок": product.get("title"),
            "Цена": product.get("price"),
            "Ссылка": product.get("url"),
            "Фото": "|".join(product.get("images", [])),
        }

        rows.append(row)

    return rows


def save_excel(products: list[dict[str, Any]]) -> str:
    os.makedirs(RESULT_DIR, exist_ok=True)

    current_date = datetime.now().strftime("%d%m%Y")
    file_path = RESULT_DIR / f"result_data_{current_date}.xlsx"
    rows = build_rows(products)

    with ExcelWriter(file_path, mode="w", engine="openpyxl") as writer:
        DataFrame(rows).to_excel(writer, sheet_name="data", index=False)

    return str(file_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Парсер объявлений Avito в Excel")
    parser.add_argument("--url", default=START_URL, help="Ссылка на магазин/профиль Avito")
    parser.add_argument("--limit", type=int, default=100, help="Количество объявлений на страницу API")
    parser.add_argument("--max-items", type=int, default=None, help="Ограничение количества объявлений для теста")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    encoded_url = quote(args.url, safe=":/?&=%")

    print("Старт сбора данных Avito")
    products = collect_products_auto(
        seller_url=encoded_url,
        limit=args.limit,
        max_items=args.max_items,
    )
    file_path = save_excel(products)

    print(f"Готово. Собрано объявлений: {len(products)}")
    print(f"Файл сохранён: {file_path}")


if __name__ == "__main__":
    main()
