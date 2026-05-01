from insight_agent.config import get_news_api_key


def test_get_news_api_key_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("NEWS_API_KEY", "test-news-key")

    assert get_news_api_key() == "test-news-key"


def test_get_news_api_key_returns_none_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    assert get_news_api_key() is None
