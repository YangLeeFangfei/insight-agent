from insight_agent.collectors.base import CollectionRequest
from insight_agent.collectors.news import collect_news_articles


def test_collect_news_articles_returns_empty_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["news"],
    )

    articles = collect_news_articles(request)

    assert articles == []
