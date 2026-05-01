from insight_agent.collectors.demo import collect_demo_articles
from insight_agent.collectors.base import CollectionRequest

def test_collect_demo_articles_returns_seed_articles() -> None:
    articles = collect_demo_articles()

    assert len(articles) == 2
    assert articles[0]["company"] == "ChatGPT"
    assert articles[1]["company"] == "Gemini"
    assert articles[0]["url"] == "https://example.com/openai-launch"


def test_collect_demo_articles_filters_by_companies() -> None:
    request = CollectionRequest(
        companies=["ChatGPT"],
        time_range="30d",
        source_types=["announcement"],
    )

    articles = collect_demo_articles(request)

    assert len(articles) == 1
    assert articles[0]["company"] == "ChatGPT"

def test_collect_demo_articles_accepts_collection_request() -> None:
    request = CollectionRequest(
        companies=["Gemini"],
        time_range="30d",
        source_types=["announcement"],
    )

    articles = collect_demo_articles(request)

    assert len(articles) == 1
    assert articles[0]["company"] == "Gemini"
