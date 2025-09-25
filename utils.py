
import re

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def is_number(s: str) -> bool:
    try:
        float(s.replace(',', '.'))
        return True
    except Exception:
        return False

def to_float(s: str) -> float:
    return float(s.replace(',', '.'))
