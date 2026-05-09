
import json

import click
from insight_agent.agent.planner import parse_query
from insight_agent.collectors.base import build_collection_request
from insight_agent.db.repository import get_run, list_runs, save_run
from pathlib import Path

from insight_agent.collectors.selector import collect_articles
from insight_agent.ingestion import load_or_collect_articles
from insight_agent.llm.analyst import analyze_articles
from insight_agent.reporting.builder import build_preview_report
from insight_agent.reporting.evidence_quality import normalize_evidence_summary
from insight_agent.llm.factory import build_llm_client
from insight_agent.agent.harness import (
    initialize_run,
    record_collection_completed,
    record_analysis_completed,
    record_report_completed,
    record_run_failed,
)



@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.option("--refresh", is_flag=True)
@click.option("--no-llm", is_flag=True)
@click.argument("query")
def search(query: str, refresh: bool, no_llm: bool) -> None:
    """Echo the incoming query."""
    use_llm = not no_llm
    result = parse_query(query)
    collection_request = build_collection_request(result)
    db_path = Path("data/insight.db")
    ingestion_result = load_or_collect_articles(
        db_path=db_path,
        companies=result["companies"],
        collection_request=collection_request,
        collect_fn=collect_articles,
        refresh=refresh,
    )
    article_records = ingestion_result.articles
    run = initialize_run(result, collection_request)
    run = record_collection_completed(run, article_records)
    save_run(db_path, run)
    click.echo(f"Run ID: {run['run_id']}")
    click.echo(f"search query: {query}")
    click.echo(f"Companies:{', '.join(result['companies'])}")
    click.echo(f"Time range: {result['time_range']}")
    click.echo(f"Metrics: {', '.join(result['metrics'])}")
    click.echo(
        f"Source types: {', '.join(result['plan_preview']['source_types'])}"
    )
    click.echo(f"Run stages: {', '.join(run['plan']['stages'])}")
    click.echo(f"Articles: {len(article_records)}")
    click.echo(f"Used cache: {ingestion_result.used_cache}")
    click.echo(f"Collected: {ingestion_result.collected_count}")

    llm_analysis = None
    if use_llm:
        try:
            llm_analysis = analyze_articles(
                query_spec=result,
                articles=article_records,
                client=build_llm_client(),
            )
        except Exception as exc:
            run = record_run_failed(run, "analysis", str(exc))
            save_run(db_path, run)
            click.echo(f"Run status: {run['status']}")
            click.echo(
                f"Trace events: {', '.join(event['event_type'] for event in run['events'])}"
            )
            raise click.ClickException(f"LLM analysis failed: {exc}") from exc

        run = record_analysis_completed(run, llm_analysis)
        save_run(db_path, run)

    report = build_preview_report(
        result,
        run,
        article_records,
        llm_analysis=llm_analysis,
    )
    run = record_report_completed(run, report)
    save_run(db_path, run)

    if use_llm:
        click.echo(f"LLM summary: {report['summary']}")
        click.echo("LLM findings:")
        for finding in report["findings"]:
            click.echo(f"- {finding}")

        click.echo("LLM evidence:")
        for evidence in report["evidence"]:
            title = evidence.get("title", "Untitled evidence")
            url = evidence.get("url", "")
            click.echo(f"- {title}: {url}")

        evidence_summary = report.get("evidence_summary")
        if evidence_summary is not None:
            evidence_quality = normalize_evidence_summary(evidence_summary)
            click.echo("Evidence quality:")
            click.echo(f"Grounded citations: {evidence_quality['grounded_citations']}")
            click.echo(f"Ungrounded citations: {evidence_quality['ungrounded_citations']}")
            click.echo(f"Duplicate citations: {evidence_quality['duplicate_citations']}")

    click.echo(f"Run status: {run['status']}")
    click.echo(
        f"Trace events: {', '.join(event['event_type'] for event in run['events'])}"
    )









@cli.command()
@click.option("--limit", default=10, type=click.IntRange(min=1), show_default=True)
@click.option("--status", "status_filter")
def runs(limit: int, status_filter: str | None) -> None:
    """List saved runs."""
    saved_runs = list_runs(Path("data/insight.db"), limit=limit, status=status_filter)

    click.echo("Run history:")
    if not saved_runs:
        click.echo("No saved runs.")
        return

    for run in saved_runs:
        click.echo(f"- {run['run_id']} | {run['status']} | {run['query']}")


@cli.command()
@click.argument("run_id")
def status(run_id: str) -> None:
    """Show a saved run status."""
    run = get_run(Path("data/insight.db"), run_id)

    if run is None:
        raise click.ClickException(f"Run not found: {run_id}")

    click.echo(f"Run ID: {run['run_id']}")
    click.echo(f"Status: {run['status']}")
    click.echo("Trace events:")
    for event in run["events"]:
        event_payload = json.dumps(event.get("payload", {}), sort_keys=True)
        click.echo(f"- {event['event_type']}: {event_payload}")


@cli.command()
@click.option("--days",default=7,type=int)
def compare(days:int) -> None:
     """Compare companies."""
     click.echo(f"compare command for {days} days")



if __name__ == "__main__":
    cli()
