from insight_agent.collectors.base import CollectionRequest
from insight_agent.config import get_news_api_key


def collect_news_articles(request: CollectionRequest) -> list[dict[str, str]]:
    api_key = get_news_api_key()

    if api_key is None:
        return []

    return []

def build_news_api_params(
    request: CollectionRequest,
    api_key: str,
) -> dict[str, str]:
    return {
        "q": " OR ".join(request.companies),
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": api_key,
    }
