from pathlib import Path
import re

def read_text(path):
    return Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""

def safe_name(value):
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)
