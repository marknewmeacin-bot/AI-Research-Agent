import os

from dotenv import load_dotenv


load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
SEARCH_URL = os.getenv("SEARCH_URL", "https://html.duckduckgo.com/html/")
