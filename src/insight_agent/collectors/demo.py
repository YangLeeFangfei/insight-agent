
def collect_demo_articles(companies: list[str] | None = None) -> list[dict[str, str]]:
    articles = [
        {
            "company": "ChatGPT",
            "title": "Launch update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "OpenAI launched a new feature for enterprise teams.",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/openai-launch",
            "sentiment": "positive",
        },
        {
            "company": "Gemini",
            "title": "Model update",
            "source_name": "Google",
            "source_type": "announcement",
            "content": "Gemini announced a model update for developers.",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T11:00:00",
            "url": "https://example.com/gemini-update",
            "sentiment": "neutral",
        }
    ]

    if not companies:
        return articles
    
    company_set = set(companies)
    return [
        article
        for article in articles
        if article["company"] in company_set
    ]



