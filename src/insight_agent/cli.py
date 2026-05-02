
import click
from insight_agent.agent.planner import parse_query
from insight_agent.collectors.base import build_collection_request
from insight_agent.agent.harness import initialize_run, record_collection_completed
from pathlib import Path

from insight_agent.collectors.selector import collect_articles
from insight_agent.db.repository import init_db, insert_article, list_articles_for_companies


@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Echo the incoming query."""
    result = parse_query(query)
    collection_request = build_collection_request(result)
    db_path = Path("data/insight.db")
    init_db(db_path)
    existing_rows = list_articles_for_companies(db_path, result["companies"])
    if not existing_rows:
        for article in collect_articles(collection_request):
            insert_article(db_path, article)
    
    matching_articles = list_articles_for_companies(db_path, result["companies"])
    article_records = [dict(row) for row in matching_articles]
    run = initialize_run(result, collection_request)
    run = record_collection_completed(run, article_records)
    click.echo(f"search query: {query}")
    click.echo(f"Companies:{', '.join(result['companies'])}")
    click.echo(f"Time range: {result['time_range']}")
    click.echo(f"Metrics: {', '.join(result['metrics'])}")
    click.echo(
        f"Source types: {', '.join(result['plan_preview']['source_types'])}"
    )
    click.echo(f"Run stages: {', '.join(run['plan']['stages'])}")
    click.echo(
        f"Trace events: {', '.join(event['event_type'] for event in run['events'])}"
    )


@cli.command()
@click.option("--days",default=7,type=int)
def compare(days:int) -> None:
     """Compare companies."""
     click.echo(f"compare command for {days} days")



if __name__ == "__main__":
    cli()
