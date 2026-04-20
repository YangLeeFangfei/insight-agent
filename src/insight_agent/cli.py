
import click
from insight_agent.agent.planner import parse_query


@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Echo the incoming query."""
    result = parse_query(query)
    click.echo(f"search query: {query}")
    click.echo(f"Companies:{', '.join(result['companies'])}")
    click.echo(f"Time range: {result['time_range']}")
    click.echo(f"Metrics: {', '.join(result['metrics'])}")
    click.echo(
        f"Source types: {', '.join(result['plan_preview']['source_types'])}"
    )

@cli.command()
@click.option("--days",default=7,type=int)
def compare(days:int) -> None:
     """Compare companies."""
     click.echo(f"compare command for {days} days")



if __name__ == "__main__":
    cli()
