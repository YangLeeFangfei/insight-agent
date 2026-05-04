from collections.abc import Callable
from pathlib import Path
from dataclasses import dataclass
from insight_agent.collectors.base import CollectionRequest
from insight_agent.db.repository import (
    init_db,
    insert_article,
    list_articles_for_companies,
)
from insight_agent.normalize.cleaner import normalize_article

@dataclass(frozen=True)
class IngestionResult:
    articles: list[dict[str, str]]
    used_cache: bool
    collected_count: int

def load_or_collect_articles(
    db_path: Path,
    companies: list[str],
    collection_request: CollectionRequest,
    collect_fn: Callable[[CollectionRequest], list[dict[str, str]]],
    refresh: bool = False,
) -> IngestionResult:
    init_db(db_path)

    existing_rows = list_articles_for_companies(db_path, companies)
    used_cache = bool(existing_rows) and not refresh
    collected_count = 0
    if not used_cache:
        collected_articles = collect_fn(collection_request)
        collected_count = len(collected_articles)

        for article in collected_articles:
            normalized_article = normalize_article(article)
            insert_article(db_path, normalized_article)

    matching_rows = list_articles_for_companies(db_path, companies)
    articles = [dict(row) for row in matching_rows]

    return IngestionResult(
        articles=articles,
        used_cache=used_cache,
        collected_count=collected_count,
    )
