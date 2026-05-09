from insight_agent.db.repository import (
    get_run,
    init_db,
    insert_article,
    list_articles,
    list_articles_for_companies,
    list_runs,
    save_run,
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

def test_repository_skips_duplicate_article_urls(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    article = {
        "company": "ChatGPT",
        "title": "Launch update",
        "source_name": "OpenAI",
        "source_type": "announcement",
        "content": "Product launch details",
        "published_date": "2026-04-20",
        "collected_at": "2026-04-20T10:00:00",
        "url": "https://example.com/openai-launch",
        "sentiment": "positive",
    }

    insert_article(db_path, article)
    insert_article(db_path, article)

    rows = list_articles(db_path)

    assert len(rows) == 1


def test_repository_saves_and_reads_run_state(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    run = {
        "run_id": "run_test",
        "status": "report_completed",
        "plan": {
            "query": "Compare ChatGPT sentiment in the last 30 days",
            "stages": ["analysis", "reporting"],
        },
        "events": [
            {
                "event_type": "run.started",
                "payload": {
                    "run_id": "run_test",
                    "query": "Compare ChatGPT sentiment in the last 30 days",
                },
            },
            {
                "event_type": "run.report_completed",
                "payload": {
                    "evidence_count": 1,
                },
            },
        ],
    }

    save_run(db_path, run)
    saved_run = get_run(db_path, "run_test")

    assert saved_run["run_id"] == "run_test"
    assert saved_run["status"] == "report_completed"
    assert saved_run["plan"]["query"] == "Compare ChatGPT sentiment in the last 30 days"
    assert saved_run["events"][1]["event_type"] == "run.report_completed"


def test_repository_lists_saved_runs(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    save_run(
        db_path,
        {
            "run_id": "run_first",
            "status": "failed",
            "plan": {
                "query": "Compare ChatGPT sentiment",
                "stages": ["analysis"],
            },
            "events": [],
        },
    )
    save_run(
        db_path,
        {
            "run_id": "run_second",
            "status": "report_completed",
            "plan": {
                "query": "Compare Gemini topics",
                "stages": ["analysis", "reporting"],
            },
            "events": [],
        },
    )

    runs = list_runs(db_path)

    assert [run["run_id"] for run in runs] == ["run_second", "run_first"]
    assert runs[0]["status"] == "report_completed"
    assert runs[0]["query"] == "Compare Gemini topics"


def test_repository_limits_saved_runs(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    for index in range(3):
        save_run(
            db_path,
            {
                "run_id": f"run_{index}",
                "status": "report_completed",
                "plan": {
                    "query": f"Query {index}",
                    "stages": ["analysis", "reporting"],
                },
                "events": [],
            },
        )

    runs = list_runs(db_path, limit=2)

    assert [run["run_id"] for run in runs] == ["run_2", "run_1"]


def test_repository_filters_saved_runs_by_status(tmp_path) -> None:
    db_path = tmp_path / "insight.db"
    init_db(db_path)

    save_run(
        db_path,
        {
            "run_id": "run_failed",
            "status": "failed",
            "plan": {
                "query": "Compare ChatGPT sentiment",
                "stages": ["analysis"],
            },
            "events": [],
        },
    )
    save_run(
        db_path,
        {
            "run_id": "run_completed",
            "status": "report_completed",
            "plan": {
                "query": "Compare Gemini topics",
                "stages": ["analysis", "reporting"],
            },
            "events": [],
        },
    )

    runs = list_runs(db_path, status="failed")

    assert [run["run_id"] for run in runs] == ["run_failed"]
