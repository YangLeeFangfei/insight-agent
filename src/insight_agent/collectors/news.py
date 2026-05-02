from insight_agent.collectors.base import CollectionRequest
from insight_agent.config import get_news_api_key
import httpx


def collect_news_articles(request: CollectionRequest) -> list[dict[str, str]]:
    api_key = get_news_api_key()

    if api_key is None:
        return []

    params = build_news_api_params(request, api_key)
    response = httpx.get(
        "https://newsapi.org/v2/everything",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return parse_news_api_articles(response.json(), request.companies[0])

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

def parse_news_api_articles(
    response_json: dict[str, object],
    company: str,
) -> list[dict[str, str]]:
    articles = []

    for item in response_json.get("articles", []):
        articles.append(
            {
                "company": company,
                "title": item["title"],
                "source_name": item["source"]["name"],
                "source_type": "news",
                "content": item["description"],
                "published_date": item["publishedAt"],
                "collected_at": item["publishedAt"],
                "url": item["url"],
                "sentiment": "neutral",
            }
        )

    return articles
