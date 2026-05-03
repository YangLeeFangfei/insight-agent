from insight_agent.collectors.base import CollectionRequest
from insight_agent.config import get_news_api_key
import httpx


def collect_news_articles(request: CollectionRequest) -> list[dict[str, str]]:
    api_key = get_news_api_key()

    if api_key is None:
        return []
    
    articles = []

    for company in request.companies:
        company_request = CollectionRequest(
            companies=[company],
            time_range=request.time_range,
            source_types=request.source_types,   
        )

        params = build_news_api_params(company_request, api_key)
        try:
            response = httpx.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            continue

        articles.extend(parse_news_api_articles(response.json(), company))
    return articles

def build_news_api_params(
    request: CollectionRequest,
    api_key: str,
) -> dict[str, str]:
    return {
        "q": request.companies[0],
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
        if not isinstance(item, dict):
            continue

        source = item.get("source")
        if not isinstance(source, dict):
            continue

        title = item.get("title")
        source_name = source.get("name")
        url = item.get("url")
        published_at = item.get("publishedAt")
        content = item.get("description") or ""

        if not title or not source_name or not url or not published_at:
            continue

        articles.append(
            {
                "company": company,
                "title": title,
                "source_name": source_name,
                "source_type": "news",
                "content": content,
                "published_date": published_at,
                "collected_at": published_at,
                "url": url,
                "sentiment": "neutral",
            }
        )

    return articles

