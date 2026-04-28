from insight_agent.db.repository import (
    init_db,
    insert_article,
    list_articles,
    list_articles_for_companies,
)


def test_repository_inserts_and_lists_articles(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)
    insert_article(
        db_path,
        {
            "company": "ChatGPT",
            "title": "Launch update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "Product launch details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/openai-launch",
            "sentiment": "positive",
        },
    )

    rows = list_articles(db_path)

    assert len(rows) == 1
    assert rows[0]["company"] == "ChatGPT"


def test_repository_filters_articles_by_company(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    insert_article(
        db_path,
        {
            "company": "ChatGPT",
            "title": "Launch update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "Product launch details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/openai-launch",
            "sentiment": "positive",
        },
    )

    insert_article(
        db_path,
        {
            "company": "Gemini",
            "title": "Model update",
            "source_name": "Google",
            "source_type": "announcement",
            "content": "Gemini update details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T11:00:00",
            "url": "https://example.com/gemini-update",
            "sentiment": "neutral",
        },
    )

    rows = list_articles_for_companies(db_path, ["ChatGPT"])

    assert len(rows) == 1
    assert rows[0]["company"] == "ChatGPT"

