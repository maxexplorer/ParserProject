# Парсер Uralsm

Парсер собирает запчасти К-700/К-744 и формирует Excel в том же формате из 46 колонок, что и `shop_uralaz_site`.

## Номер группы

Пока номер группы неизвестен, поле `Номер_группы` остаётся пустым. Позже один номер для всей группы К-700/К-744 можно указать:

- в `data/data.py` в поле `group_number`;
- аргументом `--group-number`;
- переменной окружения `URALSM_GROUP_NUMBER`.

Товары не распределяются по категориям Uralaz.

## Запуск

```powershell
venv\Scripts\python.exe uralsm_site\main.py
```

Проверка на первых двух товарах без задержки:

```powershell
venv\Scripts\python.exe uralsm_site\main.py --limit 2 --delay 0
```

Готовый файл создаётся в `uralsm_site/results`, а собранные ссылки сохраняются в `uralsm_site/data/product_data_list.json`.
