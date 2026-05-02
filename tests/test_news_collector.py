from insight_agent.collectors.base import CollectionRequest
from insight_agent.collectors.news import (
    build_news_api_params,
    collect_news_articles,
    parse_news_api_articles,
)
import httpx


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

def test_parse_news_api_articles_maps_response_to_article_dict() -> None:
    response_json = {
        "articles": [
            {
                "title": "OpenAI launches new ChatGPT feature",
                "source": {"name": "Example News"},
                "description": "OpenAI released a new feature for ChatGPT teams.",
                "url": "https://example.com/chatgpt-feature",
                "publishedAt": "2026-04-30T10:00:00Z",
            }
        ]
    }

    articles = parse_news_api_articles(response_json, "ChatGPT")

    assert len(articles) == 1
    assert articles[0]["company"] == "ChatGPT"
    assert articles[0]["title"] == "OpenAI launches new ChatGPT feature"
    assert articles[0]["source_name"] == "Example News"
    assert articles[0]["source_type"] == "news"
    assert articles[0]["content"] == "OpenAI released a new feature for ChatGPT teams."
    assert articles[0]["published_date"] == "2026-04-30T10:00:00Z"
    assert articles[0]["url"] == "https://example.com/chatgpt-feature"
    assert articles[0]["sentiment"] == "neutral"


def test_collect_news_articles_fetches_and_parses_articles(monkeypatch) -> None:
    monkeypatch.setenv("NEWS_API_KEY", "test-news-key")

    def fake_get(url, params, timeout):
        assert url == "https://newsapi.org/v2/everything"
        assert params["q"] == "ChatGPT"
        assert params["apiKey"] == "test-news-key"
        assert timeout == 10

        return httpx.Response(
            200,
            json={
                "articles": [
                    {
                        "title": "ChatGPT launches team feature",
                        "source": {"name": "Example News"},
                        "description": "ChatGPT added a feature for teams.",
                        "url": "https://example.com/chatgpt-teams",
                        "publishedAt": "2026-04-30T10:00:00Z",
                    }
                ]
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["news"],
    )

    articles = collect_news_articles(request)

    assert len(articles) == 1
    assert articles[0]["company"] == "ChatGPT"
    assert articles[0]["title"] == "ChatGPT launches team feature"




