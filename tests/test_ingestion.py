from pathlib import Path

from insight_agent.collectors.base import CollectionRequest
from insight_agent.db.repository import init_db, insert_article
from insight_agent.ingestion import load_or_collect_articles


def test_load_or_collect_articles_uses_cached_articles_without_refresh(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)
    insert_article(
        db_path,
        {
            "company": "ChatGPT",
            "title": "Cached update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "Cached product details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/cached-update",
            "sentiment": "neutral",
        },
    )

    def fake_collect_articles(collection_request):
        raise AssertionError("collector should not run when cache exists")

    result = load_or_collect_articles(
        db_path=db_path,
        companies=["ChatGPT"],
        collection_request=CollectionRequest(
            companies=["ChatGPT"],
            time_range="30d",
            source_types=["news"],
        ),
        collect_fn=fake_collect_articles,
        refresh=False,
    )

    assert len(result.articles) == 1
    assert result.articles[0]["title"] == "Cached update"
    assert result.used_cache is True
    assert result.collected_count == 0

def test_load_or_collect_articles_collects_when_refresh_is_true(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)
    insert_article(
        db_path,
        {
            "company": "ChatGPT",
            "title": "Cached update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "Cached product details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/cached-update",
            "sentiment": "neutral",
        },
    )

    def fake_collect_articles(collection_request):
        return [
            {
                "company": "ChatGPT",
                "title": " Fresh update ",
                "source_name": "OpenAI",
                "source_type": "Announcement",
                "content": " Fresh product details ",
                "published_date": "2026-05-03",
                "collected_at": "2026-05-03T10:00:00",
                "url": "https://example.com/fresh-update",
                "sentiment": "positive",
            }
        ]

    result = load_or_collect_articles(
        db_path=db_path,
        companies=["ChatGPT"],
        collection_request=CollectionRequest(
            companies=["ChatGPT"],
            time_range="30d",
            source_types=["news"],
        ),
        collect_fn=fake_collect_articles,
        refresh=True,
    )

    assert len(result.articles) == 2
    assert result.articles[0]["title"] == "Cached update"
    assert result.articles[1]["title"] == "Fresh update"
    assert result.articles[1]["source_type"] == "announcement"
    assert result.articles[1]["content"] == "Fresh product details"
    assert result.used_cache is False
    assert result.collected_count == 1

def test_load_or_collect_articles_returns_cache_metadata(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)
    insert_article(
        db_path,
        {
            "company": "ChatGPT",
            "title": "Cached update",
            "source_name": "OpenAI",
            "source_type": "announcement",
            "content": "Cached product details",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/cached-update",
            "sentiment": "neutral",
        },
    )

    def fake_collect_articles(collection_request):
        raise AssertionError("collector should not run when cache exists")

    result = load_or_collect_articles(
        db_path=db_path,
        companies=["ChatGPT"],
        collection_request=CollectionRequest(
            companies=["ChatGPT"],
            time_range="30d",
            source_types=["news"],
        ),
        collect_fn=fake_collect_articles,
        refresh=False,
    )

    assert len(result.articles) == 1
    assert result.used_cache is True
    assert result.collected_count == 0
