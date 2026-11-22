"""Write XLSX workbooks without truncating the destination on failure."""

import os
import tempfile
from pathlib import Path

from openpyxl import load_workbook


DATA_WORKBOOK = Path('data/data.xlsx')


def find_workbook(path=DATA_WORKBOOK):
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f'Не найден файл Excel «{source}».')
    return source


def open_workbook_sheet(sheet_name, path=DATA_WORKBOOK):
    source = find_workbook(path)
    workbook = load_workbook(source)
    if sheet_name not in workbook.sheetnames:
        workbook.close()
        raise ValueError(f'В книге «{source}» нет листа «{sheet_name}».')
    return workbook, workbook[sheet_name]


def save_workbook(workbook, path=DATA_WORKBOOK):
    target = Path(path)
    output = tempfile.NamedTemporaryFile(
        dir=target.parent, prefix=f'.{target.stem}-', suffix='.tmp', delete=False
    )
    temporary = Path(output.name)
    try:
        with output:
            workbook.save(output)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
