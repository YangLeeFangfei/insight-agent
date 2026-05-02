import os


def get_news_api_key() -> str | None:
    return os.getenv("NEWS_API_KEY")

def get_collector_mode() -> str:
    return os.getenv("INSIGHT_COLLECTOR", "demo")