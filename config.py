from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
WORKSPACE_DIR = BASE_DIR / "workspace"
CACHE_DIR = BASE_DIR / ".cache"

WORKSPACE_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_LLM_CALLS = 2
