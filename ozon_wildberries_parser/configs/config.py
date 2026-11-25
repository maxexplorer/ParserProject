from .secret_store import SecretStoreError, load_secrets

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
    'ping': 'https://common-api.wildberries.ru/ping',
    'upload_task': 'https://discounts-prices-api.wildberries.ru/api/v2/upload/task',
    'list_goods_filter': 'https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter',
    'products': 'https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/products',
    'warehouses': 'https://marketplace-api.wildberries.ru/api/v3/warehouses',
    'stocks': 'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}',
    'content_media': 'https://content-api.wildberries.ru/content/v3/media/save'
}

OZON_EXPIRY_WARNING_DAYS = 7
OZON_HEADERS = {
    'Client-Id': '2213525',
    'Content-Type': 'application/json',
}
WB_HEADERS = {'Content-Type': 'application/json'}
FIGMA_HEADERS = {}
API_CREDENTIALS = {
    'ozon': ('ozon_key', 'Api-Key', OZON_HEADERS),
    'wb': ('wb_key', 'Authorization', WB_HEADERS),
    'figma': ('figma_token', 'X-Figma-Token', FIGMA_HEADERS),
}


def apply_api_secrets(secrets: dict[str, str]) -> None:
    for name, header, headers in API_CREDENTIALS.values():
        if secrets.get(name):
            headers[header] = secrets[name]
        else:
            headers.pop(header, None)


SECRET_STORE_ERROR = None
try:
    apply_api_secrets(load_secrets())
except SecretStoreError as error:
    SECRET_STORE_ERROR = str(error)
