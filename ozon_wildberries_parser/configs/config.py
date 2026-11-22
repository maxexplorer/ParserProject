from configs.secret_store import load_secrets


SECRETS = load_secrets()

# configs/config.py

API_URLS_OZON = {
    'roles': 'https://api-seller.ozon.ru/v1/roles',
    'product_list': 'https://api-seller.ozon.ru/v3/product/list',
    'import_price': 'https://api-seller.ozon.ru/v1/product/import/prices',
    'product_info_prices': 'https://api-seller.ozon.ru/v5/product/info/prices',
    'analytics_data': 'https://api-seller.ozon.ru/v1/analytics/data',
    'product_info_attributes': 'https://api-seller.ozon.ru/v4/product/info/attributes',
    'product_info_stocks': 'https://api-seller.ozon.ru/v4/product/info/stocks',
    'product_pictures_import': 'https://api-seller.ozon.ru/v1/product/pictures/import'

}

API_URLS_WB = {
    'upload_task': 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task',
    'list_goods_filter': 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter',
    'products': 'https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/products',
    'warehouses': 'https://marketplace-api.wildberries.ru/api/v3/warehouses',
    'stocks': 'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}',
    'content_media': 'https://content-api.wildberries.ru/content/v3/media/save'
}

# ===== OZON =====
OZON_HEADERS = {
    'Client-Id': '2213525',
    'Api-Key': SECRETS.get('ozon_key', ''),
    'Content-Type': 'application/json',
}

# ===== WB =====

# Единый токен Wildberries

# Единые заголовки Wildberries
WB_HEADERS = {
    'Authorization': SECRETS.get('wb_key', ''),
    'Content-Type': 'application/json'
}

# ===== FIGMA =====

# Токен для FIGMA
FIGMA_TOKEN = SECRETS.get('figma_token', '')

# Заголовки для FIGMA
FIGMA_HEADERS = {
    "X-Figma-Token": FIGMA_TOKEN
}
