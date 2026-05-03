from click.testing import CliRunner

from insight_agent.cli import cli
from pathlib import Path
from insight_agent.db.repository import list_articles_for_companies

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

    

