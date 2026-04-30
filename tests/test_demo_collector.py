from insight_agent.collectors.demo import collect_demo_articles


def test_collect_demo_articles_returns_seed_articles() -> None:
    articles = collect_demo_articles()

    assert len(articles) == 2
    assert articles[0]["company"] == "ChatGPT"
    assert articles[1]["company"] == "Gemini"
    assert articles[0]["url"] == "https://example.com/openai-launch"


def test_collect_demo_articles_filters_by_companies() -> None:
    articles = collect_demo_articles(["ChatGPT"])

    assert len(articles) == 1
    assert articles[0]["company"] == "ChatGPT"
