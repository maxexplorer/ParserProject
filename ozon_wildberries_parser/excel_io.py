"""Write XLSX workbooks without truncating the destination on failure."""

import os
import tempfile
from pathlib import Path


DATA_WORKBOOK = Path('data/data.xlsx')


def find_workbook():
    if DATA_WORKBOOK.is_file():
        return DATA_WORKBOOK
    return next(
        (path for path in sorted(DATA_WORKBOOK.parent.glob('*.xlsx')) if not path.name.startswith('~$')),
        None,
    )


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
