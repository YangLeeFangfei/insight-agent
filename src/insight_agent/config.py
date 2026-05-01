import os


def get_news_api_key() -> str | None:
    return os.getenv("NEWS_API_KEY")
