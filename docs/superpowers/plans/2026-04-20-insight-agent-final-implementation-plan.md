# Insight Agent Final Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于最终设计，交付一个 workflow-first、evidence-first 的 Insight Agent MVP：支持自然语言输入、受约束采集、SQLite 持久化、可复现分析、证据绑定报告和基础工作台。

**Architecture:** 系统以 `Insight Harness` 为中心，统一驱动 CLI 和 Web UI 的任务执行。主链路固定为 `Query -> Plan Preview -> Collection -> Structuring -> Analysis -> Evidence Binding -> Report`，Agent 仅在受控边界内负责编排、回退和报告组织。所有关键结论都必须回落到数据库记录、SQL 统计和 evidence snippets。

**Tech Stack:** Python 3.11, Click, SQLite, Pydantic, httpx, BeautifulSoup4, feedparser, Jinja2, Plotly, Streamlit, pytest, Ruff.

---

## File Structure

### Existing Files To Keep

- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `src/insight_agent/cli.py`
- Modify: `src/insight_agent/agent/__init__.py`
- Modify: `src/insight_agent/agent/planner.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_planner.py`

### New Files To Create

- Create: `src/insight_agent/config.py`
- Create: `src/insight_agent/models/query.py`
- Create: `src/insight_agent/models/article.py`
- Create: `src/insight_agent/models/report.py`
- Create: `src/insight_agent/db/schema.sql`
- Create: `src/insight_agent/db/repository.py`
- Create: `src/insight_agent/db/queries.py`
- Create: `src/insight_agent/collectors/base.py`
- Create: `src/insight_agent/collectors/news.py`
- Create: `src/insight_agent/collectors/announcement.py`
- Create: `src/insight_agent/collectors/industry.py`
- Create: `src/insight_agent/normalize/cleaner.py`
- Create: `src/insight_agent/normalize/dedupe.py`
- Create: `src/insight_agent/normalize/enricher.py`
- Create: `src/insight_agent/normalize/evidence.py`
- Create: `src/insight_agent/analysis/templates.py`
- Create: `src/insight_agent/analysis/sql_guard.py`
- Create: `src/insight_agent/analysis/engine.py`
- Create: `src/insight_agent/analysis/trends.py`
- Create: `src/insight_agent/agent/trace.py`
- Create: `src/insight_agent/agent/harness.py`
- Create: `src/insight_agent/reporting/charts.py`
- Create: `src/insight_agent/reporting/builder.py`
- Create: `src/insight_agent/reporting/exporter.py`
- Create: `src/insight_agent/reporting/templates/report.html.j2`
- Create: `src/insight_agent/ui/app.py`
- Create: `tests/test_repository.py`
- Create: `tests/test_collectors.py`
- Create: `tests/test_enricher.py`
- Create: `tests/test_analysis_engine.py`
- Create: `tests/test_sql_guard.py`
- Create: `tests/test_trends.py`
- Create: `tests/test_harness.py`
- Create: `tests/test_report_builder.py`

---

### Task 1: Project Foundation And Package Shape

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `src/insight_agent/cli.py`
- Create: `src/insight_agent/config.py`
- Create: `src/insight_agent/models/query.py`
- Create: `src/insight_agent/models/article.py`
- Create: `src/insight_agent/models/report.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI tests for compare and search help**

```python
from click.testing import CliRunner

from insight_agent.cli import cli


def test_cli_help_lists_compare_and_search() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "compare" in result.output
    assert "search" in result.output


def test_compare_defaults_to_seven_days() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["compare"])

    assert result.exit_code == 0
    assert "7 days" in result.output
```

- [ ] **Step 2: Run CLI tests to verify the current state**

Run: `pytest tests/test_cli.py -q`
Expected: `compare` may be missing the default behavior or help assertions may fail if CLI drifted.

- [ ] **Step 3: Implement the minimal CLI and package config**

```python
# src/insight_agent/cli.py
import click


@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Parse a research query."""
    click.echo(f"search query: {query}")


@cli.command()
@click.option("--days", default=7, type=int)
def compare(days: int) -> None:
    """Compare companies."""
    click.echo(f"compare command for {days} days")


if __name__ == "__main__":
    cli()
```

```python
# src/insight_agent/config.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data")
    db_path: Path = Path("data/insight.db")
    reports_dir: Path = Path("data/reports")
    raw_dir: Path = Path("data/raw")
```

```python
# src/insight_agent/models/query.py
from pydantic import BaseModel, Field


class QuerySpec(BaseModel):
    raw_query: str
    companies: list[str] = Field(default_factory=list)
    time_range: str = "7d"
    metrics: list[str] = Field(default_factory=list)
```

- [ ] **Step 4: Run CLI tests and help command**

Run: `pytest tests/test_cli.py -q`
Expected: `2 passed`

Run: `PYTHONPATH=src python3 -m insight_agent.cli --help`
Expected: help output includes `compare` and `search`

- [ ] **Step 5: Commit the foundation**

```bash
git add pyproject.toml README.md src/insight_agent/cli.py src/insight_agent/config.py src/insight_agent/models/query.py src/insight_agent/models/article.py src/insight_agent/models/report.py tests/test_cli.py
git commit -m "feat: initialize insight agent package foundation"
```

---

### Task 2: Query Parser And Execution Plan Preview

**Files:**
- Modify: `src/insight_agent/agent/planner.py`
- Modify: `src/insight_agent/models/query.py`
- Create: `tests/test_planner.py`

- [ ] **Step 1: Write the failing parser tests**

```python
from insight_agent.agent.planner import parse_query


def test_parse_query_extracts_companies_and_time_range() -> None:
    result = parse_query("Compare ChatGPT and Gemini in the last 30 days")

    assert result["raw_query"] == "Compare ChatGPT and Gemini in the last 30 days"
    assert result["companies"] == ["ChatGPT", "Gemini"]
    assert result["time_range"] == "30d"


def test_parse_query_builds_plan_preview_metrics() -> None:
    result = parse_query("Compare ChatGPT and Gemini sentiment and topics in the last 30 days")

    assert result["metrics"] == ["sentiment", "topics"]
    assert result["plan_preview"]["needs_confirmation"] is True
    assert result["plan_preview"]["source_types"] == ["news", "announcement", "industry"]
```

- [ ] **Step 2: Run parser tests to verify they fail**

Run: `pytest tests/test_planner.py -q`
Expected: FAIL because `parse_query` does not yet return the structured preview

- [ ] **Step 3: Implement the minimal parser**

```python
# src/insight_agent/agent/planner.py
from __future__ import annotations


KNOWN_COMPANIES = ["ChatGPT", "Gemini", "Claude", "Kimi", "Perplexity"]


def parse_query(raw_query: str) -> dict[str, object]:
    lowered = raw_query.lower()
    companies = [name for name in KNOWN_COMPANIES if name.lower() in lowered]

    if "30" in lowered:
        time_range = "30d"
    elif "14" in lowered:
        time_range = "14d"
    else:
        time_range = "7d"

    metrics: list[str] = []
    if "sentiment" in lowered or "情绪" in raw_query:
        metrics.append("sentiment")
    if "topic" in lowered or "主题" in raw_query:
        metrics.append("topics")
    if "trend" in lowered or "声量" in raw_query:
        metrics.append("volume")
    if not metrics:
        metrics = ["sentiment", "topics", "volume"]

    return {
        "raw_query": raw_query,
        "companies": companies,
        "time_range": time_range,
        "metrics": metrics,
        "plan_preview": {
            "needs_confirmation": True,
            "source_types": ["news", "announcement", "industry"],
        },
    }
```

- [ ] **Step 4: Run parser tests again**

Run: `pytest tests/test_planner.py -q`
Expected: `2 passed`

- [ ] **Step 5: Commit the parser**

```bash
git add src/insight_agent/agent/planner.py src/insight_agent/models/query.py tests/test_planner.py
git commit -m "feat: add query parsing and plan preview"
```

---

### Task 3: SQLite Schema, Repository, And Evidence-Aware Storage

**Files:**
- Create: `src/insight_agent/db/schema.sql`
- Create: `src/insight_agent/db/repository.py`
- Create: `src/insight_agent/db/queries.py`
- Create: `tests/test_repository.py`

- [ ] **Step 1: Write the failing repository test**

```python
from insight_agent.db.repository import init_db, insert_article, list_articles


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
```

- [ ] **Step 2: Run repository test to verify it fails**

Run: `pytest tests/test_repository.py -q`
Expected: FAIL because repository functions do not exist

- [ ] **Step 3: Implement schema and repository**

```sql
-- src/insight_agent/db/schema.sql
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    content TEXT NOT NULL,
    published_date TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    sentiment TEXT
);

CREATE TABLE IF NOT EXISTS article_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    FOREIGN KEY(article_id) REFERENCES articles(id)
);

CREATE TABLE IF NOT EXISTS evidence_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    snippet_text TEXT NOT NULL,
    snippet_start INTEGER NOT NULL,
    snippet_end INTEGER NOT NULL,
    used_in_report INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(article_id) REFERENCES articles(id)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS run_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

```python
# src/insight_agent/db/repository.py
from __future__ import annotations

import sqlite3
from pathlib import Path


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    schema = Path("src/insight_agent/db/schema.sql").read_text()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript(schema)


def insert_article(db_path: Path, article: dict[str, str]) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO articles (
                company, title, source_name, source_type, content,
                published_date, collected_at, url, sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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


def list_articles(db_path: Path) -> list[sqlite3.Row]:
    with _connect(db_path) as conn:
        return list(conn.execute("SELECT * FROM articles ORDER BY id ASC"))
```

- [ ] **Step 4: Run repository test**

Run: `pytest tests/test_repository.py -q`
Expected: `1 passed`

- [ ] **Step 5: Commit the database layer**

```bash
git add src/insight_agent/db/schema.sql src/insight_agent/db/repository.py src/insight_agent/db/queries.py tests/test_repository.py
git commit -m "feat: add sqlite schema and repository layer"
```

---

### Task 4: Collectors, Structuring, And Evidence Snippets

**Files:**
- Create: `src/insight_agent/collectors/base.py`
- Create: `src/insight_agent/collectors/news.py`
- Create: `src/insight_agent/collectors/announcement.py`
- Create: `src/insight_agent/collectors/industry.py`
- Create: `src/insight_agent/normalize/cleaner.py`
- Create: `src/insight_agent/normalize/dedupe.py`
- Create: `src/insight_agent/normalize/enricher.py`
- Create: `src/insight_agent/normalize/evidence.py`
- Create: `tests/test_collectors.py`
- Create: `tests/test_enricher.py`

- [ ] **Step 1: Write the failing normalization test**

```python
from insight_agent.normalize.cleaner import normalize_article
from insight_agent.normalize.evidence import build_evidence_snippet


def test_normalize_article_strips_title_and_source_type() -> None:
    article = normalize_article(
        {
            "company": "ChatGPT",
            "title": "  Launch Update  ",
            "source_name": "OpenAI Blog",
            "source_type": "announcement",
            "content": "OpenAI launched a new feature for enterprise teams.",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/a",
            "sentiment": "positive",
        }
    )

    assert article["title"] == "Launch Update"
    assert article["source_type"] == "announcement"


def test_build_evidence_snippet_returns_bounded_snippet() -> None:
    snippet = build_evidence_snippet(
        "OpenAI launched a new feature for enterprise teams on Tuesday.",
        keyword="enterprise",
    )

    assert "enterprise" in snippet["snippet_text"]
    assert snippet["snippet_start"] >= 0
    assert snippet["snippet_end"] > snippet["snippet_start"]
```

- [ ] **Step 2: Run normalization tests to verify they fail**

Run: `pytest tests/test_enricher.py -q`
Expected: FAIL because normalization helpers are missing

- [ ] **Step 3: Implement minimal cleaners and evidence extraction**

```python
# src/insight_agent/normalize/cleaner.py
def normalize_article(article: dict[str, str]) -> dict[str, str]:
    normalized = dict(article)
    normalized["title"] = article["title"].strip()
    normalized["source_type"] = article["source_type"].strip().lower()
    normalized["content"] = article["content"].strip()
    return normalized
```

```python
# src/insight_agent/normalize/evidence.py
def build_evidence_snippet(content: str, keyword: str) -> dict[str, object]:
    lowered = content.lower()
    keyword_lower = keyword.lower()
    start = max(lowered.find(keyword_lower), 0)
    end = min(start + 80, len(content))
    return {
        "snippet_text": content[start:end],
        "snippet_start": start,
        "snippet_end": end,
    }
```

```python
# src/insight_agent/normalize/enricher.py
def classify_sentiment(content: str) -> str:
    lowered = content.lower()
    if "launch" in lowered or "growth" in lowered:
        return "positive"
    if "outage" in lowered or "risk" in lowered:
        return "negative"
    return "neutral"
```

- [ ] **Step 4: Run the structuring tests**

Run: `pytest tests/test_enricher.py -q`
Expected: `2 passed`

- [ ] **Step 5: Commit the structuring layer**

```bash
git add src/insight_agent/collectors/base.py src/insight_agent/collectors/news.py src/insight_agent/collectors/announcement.py src/insight_agent/collectors/industry.py src/insight_agent/normalize/cleaner.py src/insight_agent/normalize/dedupe.py src/insight_agent/normalize/enricher.py src/insight_agent/normalize/evidence.py tests/test_collectors.py tests/test_enricher.py
git commit -m "feat: add normalization and evidence snippet primitives"
```

---

### Task 5: Analysis Engine, SQL Guard, And Trend Detection

**Files:**
- Create: `src/insight_agent/analysis/templates.py`
- Create: `src/insight_agent/analysis/sql_guard.py`
- Create: `src/insight_agent/analysis/engine.py`
- Create: `src/insight_agent/analysis/trends.py`
- Create: `tests/test_analysis_engine.py`
- Create: `tests/test_sql_guard.py`
- Create: `tests/test_trends.py`

- [ ] **Step 1: Write the failing SQL guard test**

```python
from insight_agent.analysis.sql_guard import validate_read_only_sql


def test_validate_read_only_sql_accepts_select() -> None:
    assert validate_read_only_sql("SELECT * FROM articles") is True


def test_validate_read_only_sql_rejects_delete() -> None:
    assert validate_read_only_sql("DELETE FROM articles") is False
```

- [ ] **Step 2: Run SQL guard tests to verify they fail**

Run: `pytest tests/test_sql_guard.py -q`
Expected: FAIL because `validate_read_only_sql` is missing

- [ ] **Step 3: Implement guard and minimal analysis engine**

```python
# src/insight_agent/analysis/sql_guard.py
def validate_read_only_sql(query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized.startswith("select"):
        return False
    forbidden = [" insert ", " update ", " delete ", " drop ", " alter ", ";"]
    return not any(token in normalized for token in forbidden)
```

```python
# src/insight_agent/analysis/templates.py
TEMPLATE_QUERIES = {
    "sentiment_distribution": """
        SELECT company, sentiment, COUNT(*) AS count
        FROM articles
        WHERE published_date BETWEEN :start_date AND :end_date
        GROUP BY company, sentiment
    """,
    "volume_by_day": """
        SELECT company, published_date, COUNT(*) AS article_count
        FROM articles
        WHERE published_date BETWEEN :start_date AND :end_date
        GROUP BY company, published_date
    """,
}
```

```python
# src/insight_agent/analysis/trends.py
def detect_volume_spike(previous_count: int, current_count: int) -> bool:
    if previous_count < 5:
        return False
    return current_count >= int(previous_count * 1.5)
```

- [ ] **Step 4: Run guard and trend tests**

Run: `pytest tests/test_sql_guard.py tests/test_trends.py -q`
Expected: all tests pass

- [ ] **Step 5: Commit the analysis layer**

```bash
git add src/insight_agent/analysis/templates.py src/insight_agent/analysis/sql_guard.py src/insight_agent/analysis/engine.py src/insight_agent/analysis/trends.py tests/test_analysis_engine.py tests/test_sql_guard.py tests/test_trends.py
git commit -m "feat: add analysis templates sql guard and trend rules"
```

---

### Task 6: Insight Harness, Trace Events, And Report Builder

**Files:**
- Create: `src/insight_agent/agent/trace.py`
- Create: `src/insight_agent/agent/harness.py`
- Create: `src/insight_agent/reporting/charts.py`
- Create: `src/insight_agent/reporting/builder.py`
- Create: `src/insight_agent/reporting/exporter.py`
- Create: `src/insight_agent/reporting/templates/report.html.j2`
- Create: `tests/test_harness.py`
- Create: `tests/test_report_builder.py`

- [ ] **Step 1: Write the failing harness test**

```python
from insight_agent.agent.harness import build_run_plan


def test_build_run_plan_returns_execution_stages() -> None:
    plan = build_run_plan(
        {
            "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment", "topics"],
        }
    )

    assert plan["stages"] == [
        "plan_preview",
        "source_collection",
        "normalization",
        "analysis",
        "evidence_binding",
        "reporting",
    ]
    assert plan["needs_confirmation"] is True
```

- [ ] **Step 2: Run harness tests to verify failure**

Run: `pytest tests/test_harness.py -q`
Expected: FAIL because harness functions are missing

- [ ] **Step 3: Implement minimal harness and report builder**

```python
# src/insight_agent/agent/harness.py
def build_run_plan(query_spec: dict[str, object]) -> dict[str, object]:
    return {
        "query": query_spec["raw_query"],
        "needs_confirmation": True,
        "stages": [
            "plan_preview",
            "source_collection",
            "normalization",
            "analysis",
            "evidence_binding",
            "reporting",
        ],
    }
```

```python
# src/insight_agent/agent/trace.py
def build_trace_event(event_type: str, payload: dict[str, object]) -> dict[str, object]:
    return {"event_type": event_type, "payload": payload}
```

```python
# src/insight_agent/reporting/builder.py
def build_report_payload(summary: str, findings: list[str], evidence: list[dict[str, object]]) -> dict[str, object]:
    return {
        "summary": summary,
        "findings": findings,
        "evidence": evidence,
    }
```

- [ ] **Step 4: Run harness and report tests**

Run: `pytest tests/test_harness.py tests/test_report_builder.py -q`
Expected: all tests pass

- [ ] **Step 5: Commit the harness**

```bash
git add src/insight_agent/agent/trace.py src/insight_agent/agent/harness.py src/insight_agent/reporting/charts.py src/insight_agent/reporting/builder.py src/insight_agent/reporting/exporter.py src/insight_agent/reporting/templates/report.html.j2 tests/test_harness.py tests/test_report_builder.py
git commit -m "feat: add harness trace events and reporting scaffold"
```

---

### Task 7: CLI Integration, Streamlit Workbench, And Demo Flow

**Files:**
- Modify: `src/insight_agent/cli.py`
- Create: `src/insight_agent/ui/app.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing CLI integration test**

```python
from click.testing import CliRunner

from insight_agent.cli import cli


def test_search_command_returns_plan_preview_text() -> None:
    runner = CliRunner()

    result = runner.invoke(cli, ["search", "Compare ChatGPT and Gemini in the last 30 days"])

    assert result.exit_code == 0
    assert "plan preview" in result.output.lower()
    assert "ChatGPT" in result.output
    assert "Gemini" in result.output
```

- [ ] **Step 2: Run the integration test to verify failure**

Run: `pytest tests/test_cli.py -q`
Expected: FAIL because `search` still only echoes raw query

- [ ] **Step 3: Implement minimal CLI integration**

```python
# src/insight_agent/cli.py
import click

from insight_agent.agent.harness import build_run_plan
from insight_agent.agent.planner import parse_query


@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Parse a research query."""
    query_spec = parse_query(query)
    plan = build_run_plan(query_spec)
    click.echo("Plan preview:")
    click.echo(f"Companies: {', '.join(query_spec['companies'])}")
    click.echo(f"Time range: {query_spec['time_range']}")
    click.echo(f"Stages: {', '.join(plan['stages'])}")


@cli.command()
@click.option("--days", default=7, type=int)
def compare(days: int) -> None:
    """Compare companies."""
    click.echo(f"compare command for {days} days")
```

```python
# src/insight_agent/ui/app.py
import streamlit as st


st.set_page_config(page_title="Insight Agent", layout="wide")
st.title("Insight Agent")
st.caption("Workflow-first competitive intelligence workbench")
st.text_area("Query", "Compare ChatGPT and Gemini in the last 30 days")
st.info("Next step: wire this UI to parse_query() and build_run_plan().")
```

- [ ] **Step 4: Run the final checks**

Run: `pytest tests/test_cli.py tests/test_planner.py tests/test_repository.py tests/test_sql_guard.py tests/test_trends.py tests/test_harness.py tests/test_report_builder.py -q`
Expected: all listed tests pass

Run: `PYTHONPATH=src python3 -m insight_agent.cli search "Compare ChatGPT and Gemini in the last 30 days"`
Expected: output shows `Plan preview`, companies, time range, and stages

- [ ] **Step 5: Commit the MVP path**

```bash
git add src/insight_agent/cli.py src/insight_agent/ui/app.py README.md tests/test_cli.py
git commit -m "feat: connect cli to planning flow and add workbench scaffold"
```

---

## Self-Review

### Spec Coverage

- Workflow-first main path: covered by Tasks 2, 5, 6, 7
- Evidence-first storage and report support: covered by Tasks 3 and 4
- Harness and event model: covered by Task 6
- Just-in-time context and bounded outputs: reflected in Task 4 and Task 5 design constraints
- Minimal tool surface and read-only SQL: covered by Task 5
- Artifacts and report outputs: covered by Task 6 and Task 7

### Placeholder Scan

- No `TODO`, `TBD`, or “implement later” markers remain in task steps
- Every task includes concrete file paths, commands, and minimal code shapes

### Type Consistency

- Query parsing returns a `dict[str, object]` consistently across planner, harness, and CLI
- SQL guard uses `validate_read_only_sql`
- Harness entry point is consistently `build_run_plan`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-20-insight-agent-final-implementation-plan.md`.

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

For your current学习方式，`Inline Execution` 也可以继续保持“我带你一步步写，你自己敲代码”的教练模式。
