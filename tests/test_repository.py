from insight_agent.db.repository import init_db, insert_article, list_articles

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