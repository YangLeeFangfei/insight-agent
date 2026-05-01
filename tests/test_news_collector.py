from insight_agent.collectors.base import CollectionRequest
from insight_agent.collectors.news import (
    build_news_api_params,
    collect_news_articles,
)


def test_collect_news_articles_returns_empty_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["news"],
    )

    articles = collect_news_articles(request)

    assert articles == []

def test_build_news_api_params_uses_collection_request() -> None:
    request = CollectionRequest(
        companies=["ChatGPT", "Gemini"],
        time_range="30d",
        source_types=["news"],
    )

    params = build_news_api_params(request, "test-news-key")

    assert params["q"] == "ChatGPT OR Gemini"
    assert params["language"] == "en"
    assert params["sortBy"] == "publishedAt"
    assert params["apiKey"] == "test-news-key"
