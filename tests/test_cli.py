from click.testing import CliRunner
import pytest

from insight_agent.cli import cli
from pathlib import Path
from insight_agent.db.repository import (
    get_run,
    init_db,
    insert_article,
    list_articles_for_companies,
    save_run,
)
from insight_agent.llm.factory import FakeLLMClient, build_llm_client
from insight_agent.llm.client import OpenAICompatibleLLMClient


@pytest.fixture(autouse=True)
def clear_llm_environment(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)



def test_cli_help_shows_commands() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Insight Agent CLI." in result.output
    assert "search" in result.output


def test_status_outputs_saved_run_state() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        db_path = Path("data/insight.db")
        init_db(db_path)
        save_run(
            db_path,
            {
                "run_id": "run_test",
                "status": "report_completed",
                "plan": {
                    "query": "Compare ChatGPT sentiment in the last 30 days",
                    "stages": ["analysis", "reporting"],
                },
                "events": [
                    {
                        "event_type": "run.started",
                        "payload": {"run_id": "run_test"},
                    },
                    {
                        "event_type": "run.report_completed",
                        "payload": {"evidence_count": 1},
                    },
                ],
            },
        )

        result = runner.invoke(cli, ["status", "run_test"])

    assert result.exit_code == 0
    assert "Run ID: run_test" in result.output
    assert "Status: report_completed" in result.output
    assert "run.started" in result.output
    assert "run.report_completed" in result.output
    assert "evidence_count" in result.output
    assert "1" in result.output


def test_status_fails_when_run_does_not_exist() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        init_db(Path("data/insight.db"))

        result = runner.invoke(cli, ["status", "run_missing"])

    assert result.exit_code == 1
    assert "Run not found: run_missing" in result.output

def test_search_outputs_parsed_query_details() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["search", "Compare ChatGPT and Gemini sentiment and topics in the last 30 days"],
        )

    assert result.exit_code == 0
    assert "Run ID: run_" in result.output
    assert "ChatGPT" in result.output
    assert "Gemini" in result.output
    assert "30d" in result.output
    assert "sentiment, topics" in result.output
    assert "source_collection" in result.output
    assert "run.started" in result.output
    assert "run.plan_generated" in result.output
    assert "run.collection_requested" in result.output
    assert "run.collection_completed" in result.output
    assert "run.analysis_completed" in result.output
    assert "Articles:" in result.output
    assert "run.report_completed" in result.output
    assert "Run status: report_completed" in result.output



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

def test_search_outputs_structured_llm_report_by_default(monkeypatch) -> None:
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
    assert "Evidence quality:" in result.output
    assert "Grounded citations: 1" in result.output
    assert "Ungrounded citations: 0" in result.output
    assert "Duplicate citations: 0" in result.output
    assert "run.analysis_completed" in result.output
    assert "Run status: report_completed" in result.output
    assert "run.report_completed" in result.output


def test_search_persists_run_state(monkeypatch) -> None:
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
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )
        run_id_line = next(
            line for line in result.output.splitlines()
            if line.startswith("Run ID: ")
        )
        run_id = run_id_line.removeprefix("Run ID: ")
        saved_run = get_run(Path("data/insight.db"), run_id)

    assert result.exit_code == 0
    assert saved_run["run_id"] == run_id
    assert saved_run["status"] == "report_completed"
    assert saved_run["events"][-1]["event_type"] == "run.report_completed"


def test_search_persists_run_state_after_each_stage(monkeypatch) -> None:
    runner = CliRunner()
    saved_statuses = []

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

    def fake_save_run(db_path, run):
        saved_statuses.append(run["status"])

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)
    monkeypatch.setattr("insight_agent.cli.save_run", fake_save_run)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "search",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )

    assert result.exit_code == 0
    assert saved_statuses == [
        "collection_completed",
        "analysis_completed",
        "report_completed",
    ]


def test_search_defaults_missing_evidence_quality_counts(monkeypatch) -> None:
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

    def fake_build_preview_report(
        query_spec,
        run,
        articles,
        llm_analysis=None,
    ):
        return {
            "summary": "LLM summary.",
            "findings": [],
            "evidence": [],
            "evidence_summary": {
                "grounded_citations": 1,
            },
        }

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)
    monkeypatch.setattr(
        "insight_agent.cli.build_preview_report",
        fake_build_preview_report,
    )

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "search",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )

    assert result.exit_code == 0
    assert "Grounded citations: 1" in result.output
    assert "Ungrounded citations: 0" in result.output
    assert "Duplicate citations: 0" in result.output


def test_search_no_llm_skips_llm_analysis(monkeypatch) -> None:
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
                "--no-llm",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )

    assert result.exit_code == 0
    assert "LLM summary:" not in result.output
    assert "run.analysis_completed" not in result.output
    assert "run.report_completed" in result.output
    assert "Run status: report_completed" in result.output


def test_search_records_failed_run_when_default_llm_analysis_raises(monkeypatch) -> None:
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

    def fake_analyze_articles(query_spec, articles, client):
        raise RuntimeError("model timeout")

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)
    monkeypatch.setattr("insight_agent.cli.analyze_articles", fake_analyze_articles)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "search",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )

    assert result.exit_code == 1
    assert "Run status: failed" in result.output
    assert "run.failed" in result.output
    assert "LLM analysis failed: model timeout" in result.output


def test_search_persists_failed_run_state(monkeypatch) -> None:
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

    def fake_analyze_articles(query_spec, articles, client):
        raise RuntimeError("model timeout")

    monkeypatch.setattr("insight_agent.cli.collect_articles", fake_collect_articles)
    monkeypatch.setattr("insight_agent.cli.analyze_articles", fake_analyze_articles)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "search",
                "Compare ChatGPT sentiment in the last 30 days",
            ],
        )
        run_id_line = next(
            line for line in result.output.splitlines()
            if line.startswith("Run ID: ")
        )
        run_id = run_id_line.removeprefix("Run ID: ")
        saved_run = get_run(Path("data/insight.db"), run_id)

    assert result.exit_code == 1
    assert saved_run["status"] == "failed"
    assert saved_run["events"][-1]["event_type"] == "run.failed"
    assert saved_run["events"][-1]["payload"]["error_message"] == "model timeout"




def test_build_llm_client_returns_fake_client_without_api_key(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)

    client = build_llm_client()

    assert isinstance(client, FakeLLMClient)


def test_build_llm_client_returns_openai_compatible_client_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-llm-key")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setenv("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    client = build_llm_client()

    assert isinstance(client, OpenAICompatibleLLMClient)
    assert client.model == "mimo-v2.5"
