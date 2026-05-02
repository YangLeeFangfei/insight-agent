from insight_agent.collectors.base import CollectionRequest
from insight_agent.collectors.selector import collect_articles

def test_collect_articles_uses_demo_collector_by_default(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INSIGHT_COLLECTOR", raising=False)
    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["news"],
    )

    articles = collect_articles(request)

    assert len(articles) == 1
    assert articles[0]["company"] == "ChatGPT"

def test_collect_articles_uses_news_collector_when_configured(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INSIGHT_COLLECTOR", "news")
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["news"],
    )

    articles = collect_articles(request)

    assert articles == []