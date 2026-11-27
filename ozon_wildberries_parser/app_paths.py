import sys
from pathlib import Path


# PyInstaller exposes the launched executable separately from its unpacked modules.
APP_DIR = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
DATA_DIR = APP_DIR / 'data'
FIGMA_DATA_DIR = APP_DIR / 'figma_data'
