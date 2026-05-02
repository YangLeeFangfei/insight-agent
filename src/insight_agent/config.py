import os
from pathlib import Path

from dotenv import load_dotenv

def _load_env() -> None:
    load_dotenv(dotenv_path=Path(".env"), override=False)

def get_news_api_key() -> str | None:
    _load_env()
    return os.getenv("NEWS_API_KEY")

def get_collector_mode() -> str:
    _load_env()
    return os.getenv("INSIGHT_COLLECTOR", "demo")

