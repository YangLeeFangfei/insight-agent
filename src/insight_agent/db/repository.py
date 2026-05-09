
import json
import sqlite3
from pathlib import Path

def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema = schema_path.read_text()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(db_path) as conn:
        conn.executescript(schema)

def insert_article(db_path: Path, article: dict[str, str]) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            '''
            INSERT OR IGNORE INTO articles (
                company, title, source_name, source_type, content,
                published_date, collected_at, url, sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                article["company"],
                article["title"],
                article["source_name"],
                article["source_type"],
                article["content"],
                article["published_date"],
                article["collected_at"],
                article["url"],
                article["sentiment"],
            ),
        )

def list_articles(db_path: Path):
    with _connect(db_path) as conn:
        return list(conn.execute("SELECT * FROM articles ORDER BY id ASC"))

def list_articles_for_companies(db_path: Path, companies: list[str], ) -> list[sqlite3.Row]:
    placeholders = ", ".join(["?"] * len(companies))

    with _connect(db_path) as conn:
        return list(
            conn.execute(
                f"""
                SELECT *
                FROM articles
                WHERE company IN ({placeholders})
                ORDER BY id ASC
                """,
                tuple(companies),
            )
        )


def save_run(db_path: Path, run: dict[str, object]) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO runs (
                run_id, status, query, plan_json, events_json
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                status = excluded.status,
                query = excluded.query,
                plan_json = excluded.plan_json,
                events_json = excluded.events_json
            """,
            (
                run["run_id"],
                run["status"],
                run["plan"]["query"],
                json.dumps(run["plan"]),
                json.dumps(run["events"]),
            ),
        )


def get_run(db_path: Path, run_id: str) -> dict[str, object] | None:
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT run_id, status, query, plan_json, events_json
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "run_id": row["run_id"],
        "status": row["status"],
        "plan": json.loads(row["plan_json"]),
        "events": json.loads(row["events_json"]),
    }


def list_runs(
    db_path: Path,
    limit: int = 10,
    status: str | None = None,
) -> list[dict[str, str]]:
    with _connect(db_path) as conn:
        if status is None:
            rows = list(
                conn.execute(
                    """
                    SELECT run_id, status, query
                    FROM runs
                    ORDER BY rowid DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            )
        else:
            rows = list(
                conn.execute(
                    """
                    SELECT run_id, status, query
                    FROM runs
                    WHERE status = ?
                    ORDER BY rowid DESC
                    LIMIT ?
                    """,
                    (status, limit),
                )
            )

    return [
        {
            "run_id": row["run_id"],
            "status": row["status"],
            "query": row["query"],
        }
        for row in rows
    ]
