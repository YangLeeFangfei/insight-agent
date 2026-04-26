from click.testing import CliRunner

from insight_agent.cli import cli


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
    

