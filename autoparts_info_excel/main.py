import os
import glob
import pandas as pd


def process_excel_file(path: str) -> dict:
    """
    Parses the invoice into two blocks:
    1) summary: totals from item rows
    2) serials: article + serial rows, with blanks for items without serial details
    """
    df: pd.DataFrame = pd.read_excel(path, header=None)

    name_col = 1
    serial_article_col = 2
    serial_col = 8
    item_article_col = 5
    qty_col = 6
    price_col = 7

    col_name = '\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435'
    col_article = '\u0410\u0440\u0442\u0438\u043a\u0443\u043b'
    col_quantity = '\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e'
    col_price = '\u0426\u0435\u043d\u0430'
    col_series = '\u0421\u0435\u0440\u0438\u044f'

    def get_article(value) -> str | None:
        if pd.isna(value):
            return None

        article = str(value).strip()
        return article if article.startswith('BNN') else None

    def get_number(value) -> float | None:
        if pd.isna(value):
            return None

        try:
            return float(str(value).replace(' ', '').replace(',', '.'))
        except Exception:
            return None

    summary_by_article = {}

    # Item rows: article in F, quantity in G, price in H.
    for i in range(len(df)):
        row = df.iloc[i]
        article = get_article(row[item_article_col])

        if not article:
            continue

        quantity = get_number(row[qty_col]) or 0
        price = get_number(row[price_col])
        name = str(row[name_col]).strip() if pd.notna(row[name_col]) else None

        if article not in summary_by_article:
            summary_by_article[article] = {
                col_name: name,
                col_article: article,
                col_quantity: 0,
                col_price: price,
            }

        summary_by_article[article][col_quantity] += quantity

        if summary_by_article[article][col_name] is None and name:
            summary_by_article[article][col_name] = name

        if summary_by_article[article][col_price] is None and price is not None:
            summary_by_article[article][col_price] = price

    summary = []
    for row in summary_by_article.values():
        quantity = row[col_quantity]
        row[col_quantity] = int(quantity) if float(quantity).is_integer() else quantity
        summary.append(row)

    serial_count_by_article = {}

    # First count real serial rows: article in C, serial in I.
    for i in range(len(df)):
        row = df.iloc[i]
        article = get_article(row[serial_article_col])

        if article:
            serial_count_by_article[article] = serial_count_by_article.get(article, 0) + 1

    serial_rows = []
    added_blank_serials = {}

    # Build serial output in source order. Some item rows have no serial
    # breakdown, so blank serials are inserted at the item row, not at the end.
    for i in range(len(df)):
        row = df.iloc[i]
        item_article = get_article(row[item_article_col])

        if item_article:
            quantity = int(get_number(row[qty_col]) or 0)
            real_serials = serial_count_by_article.get(item_article, 0)
            already_added = added_blank_serials.get(item_article, 0)
            missing = max(quantity - real_serials - already_added, 0)

            for _ in range(missing):
                serial_rows.append({
                    col_article: item_article,
                    col_series: None,
                })

            added_blank_serials[item_article] = already_added + missing

        serial_article = get_article(row[serial_article_col])

        if serial_article:
            series = str(row[serial_col]).strip() if pd.notna(row[serial_col]) else None
            serial_rows.append({
                col_article: serial_article,
                col_series: series,
            })

    return {'summary': summary, 'serials': serial_rows}

def save_result(processed: dict, source_file: str) -> None:
    """
    Writes both result blocks to one sheet:
    - summary: columns A-D
    - serials: columns G-H
    """
    os.makedirs('results', exist_ok=True)
    base_name = os.path.basename(source_file).rsplit('.', 1)[0]
    out_path = f'results/{base_name}_result_data.xlsx'

    df_summary = pd.DataFrame(processed['summary'])
    df_serials = pd.DataFrame(processed['serials'])
    sheet_name = '\u041b\u0438\u0441\u04421'

    with pd.ExcelWriter(out_path) as writer:
        df_summary.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name,
            startrow=0,
            startcol=0
        )

        df_serials.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name,
            startrow=0,
            startcol=6
        )

    print(f'Result saved: {out_path}')


def main(folder: str = 'data') -> None:
    """
    Processes all Excel files from the data folder.
    """
    files = glob.glob(os.path.join(folder, '*.xls')) + glob.glob(os.path.join(folder, '*.xlsx'))

    if not files:
        print('No Excel files found in data/ (.xls or .xlsx)')
        return

    for file in files:
        print(f'Processing: {file}')
        processed = process_excel_file(file)
        save_result(processed, file)


if __name__ == '__main__':
    main()
