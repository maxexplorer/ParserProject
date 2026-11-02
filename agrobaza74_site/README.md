# Парсер Agrobaza74

Парсер собирает запчасти К-700/К-744 и формирует Excel в том же формате из 46 колонок, что и `shop_uralaz_site`.

## Настройка

Перед итоговой выгрузкой укажите номер группы клиента одним из способов:

- в `data/data.py` в поле `group_number`;
- аргументом `--group-number`;
- переменной окружения `AGROBAZA_GROUP_NUMBER`.

Шаблоны поля `Поисковые_запросы` находятся в `data/data.py`. Модель техники извлекается из названия товара автоматически. Если модель в названии не найдена, используются `default_models` категории.

## Запуск

```powershell
python agrobaza74_site/main.py --group-number 123456
```

Проверка на первых двух товарах без задержки:

```powershell
python agrobaza74_site/main.py --limit 2 --delay 0 --group-number 123456
```

Готовый файл создаётся в `agrobaza74_site/results`, а собранные ссылки сохраняются в `agrobaza74_site/data/product_data_list.json`.
