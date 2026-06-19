import hashlib
from config import CACHE_DIR

def _key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def load_cached(command: str):
    path = CACHE_DIR / _key(command)
    return path.read_text() if path.exists() else None

def save_cached(command: str, content: str):
    path = CACHE_DIR / _key(command)
    path.write_text(content)

def load_last_good(command: str):
    path = CACHE_DIR / (_key(command) + ".good")
    return path.read_text() if path.exists() else None

def save_last_good(command: str, content: str):
    path = CACHE_DIR / (_key(command) + ".good")
    path.write_text(content)
