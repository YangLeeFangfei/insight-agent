from click.testing import CliRunner

from insight_agent.cli import cli
from pathlib import Path
from insight_agent.db.repository import (
    init_db,
    insert_article,
    list_articles_for_companies,
)
from insight_agent.llm.factory import FakeLLMClient, build_llm_client
from insight_agent.llm.client import OpenAICompatibleLLMClient



def test_cli_help_shows_commands() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Insight Agent CLI." in result.output
    assert "search" in result.output

def test_search_outputs_parsed_query_details() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["search", "Compare ChatGPT and Gemini sentiment and topics in the last 30 days"],
    )

    assert result.exit_code == 0
    assert "ChatGPT" in result.output
    assert "Gemini" in result.output
    assert "30d" in result.output
    assert "sentiment, topics" in result.output
    assert "source_collection" in result.output
    assert "run.started" in result.output
    assert "run.plan_generated" in result.output
    assert "run.collection_requested" in result.output
    assert "run.collection_completed" in result.output
    assert "Articles:" in result.output



def test_search_normalizes_collected_articles_before_inserting(monkeypatch) -> None:
    runner = CliRunner()

    def fake_collect_articles(collection_request):
        return [
            {
                "company": "ChatGPT",
                "title": "  Launch Update  ",
                "source_name": "OpenAI",
                "source_type": "Announcement",
                "content": "  Product launch details  ",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            }
        ]

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["search", "Compare ChatGPT sentiment in the last 30 days"],
        )
        rows = list_articles_for_companies(Path("data/insight.db"), ["ChatGPT"])

    assert result.exit_code == 0
    assert len(rows) == 1
    assert rows[0]["title"] == "Launch Update"
    assert rows[0]["source_type"] == "announcement"
    assert rows[0]["content"] == "Product launch details"

def test_search_refresh_collects_even_when_cached_articles_exist(monkeypatch) -> None:
    runner = CliRunner()

    def fake_collect_articles(collection_request):
        return [
            {
                "company": "ChatGPT",
                "title": "Fresh update",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": "Fresh product launch details",
                "published_date": "2026-05-03",
                "collected_at": "2026-05-03T10:00:00",
                "url": "https://example.com/fresh-update",
                "sentiment": "positive",
            }
        ]

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)

    with runner.isolated_filesystem():
        db_path = Path("data/insight.db")
        init_db(db_path)
        insert_article(
            db_path,
            {
                "company": "ChatGPT",
                "title": "Old update",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": "Old product launch details",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/old-update",
                "sentiment": "neutral",
            },
        )

        result = runner.invoke(
            cli,
            [
                "search",
                "--refresh",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )
        rows = list_articles_for_companies(db_path, ["ChatGPT"])

    assert result.exit_code == 0
    assert len(rows) == 2
    assert rows[0]["title"] == "Old update"
    assert rows[1]["title"] == "Fresh update"

def test_cli_search_uses_ingestion_pipeline() -> None:
    cli_source = Path("src/insight_agent/cli.py").read_text()

    assert "load_or_collect_articles" in cli_source
    assert "collect_fn=collect_articles" in cli_source

def test_search_llm_outputs_structured_llm_report(monkeypatch) -> None:
    runner = CliRunner()

    def fake_collect_articles(collection_request):
        return [
            {
                "company": "ChatGPT",
                "title": "Launch update",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": "ChatGPT launched a new enterprise feature.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            }
        ]

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "search",
                "--llm",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )

    assert result.exit_code == 0
    assert "LLM summary:" in result.output
    assert "LLM findings:" in result.output
    assert "- LLM finding: ChatGPT has more enterprise-facing updates." in result.output
    assert "- LLM risk: Evidence set is small." in result.output
    assert "LLM evidence:" in result.output
    assert "- Launch update: https://example.com/openai-launch" in result.output


def test_build_llm_client_returns_fake_client_without_api_key(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    client = build_llm_client()

    assert isinstance(client, FakeLLMClient)


def test_build_llm_client_returns_openai_compatible_client_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-llm-key")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setenv("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    client = build_llm_client()

    assert isinstance(client, OpenAICompatibleLLMClient)
    assert client.model == "mimo-v2.5"

