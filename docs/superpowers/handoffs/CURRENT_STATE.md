# Insight Agent Current State

## Purpose

This file is the always-current project status board.

Use it when:

- starting a new Codex session
- quickly checking where the build stopped
- deciding the single next action

If detailed local reasoning from the last thread is needed, read the latest handoff file after this one.

## Current Phase

Current main-track phase:

- `Harness -> Report` moving toward `data-backed report preview`

Current sub-goal:

- make `report preview` use real SQLite article content instead of static strings

## Main Track Status

### Completed

- `Query -> Plan`
- `Data -> SQLite`
- `Normalize -> Evidence`
- `Analysis -> Trends`
- `Harness -> Trace`
- `Streamlit UI scaffold`
- `UI run preview`
- `SQLite-backed matching articles in UI`

### In Progress

- `Report Preview -> data-backed generation`

### Not Yet Started

- real collector integration
- data-backed findings/trend summaries
- HTML report export
- richer UI workbench layout

## Current Working Artifacts

### Query / Run

- [planner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/planner.py:1)
- [harness.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/harness.py:1)
- [trace.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/trace.py:1)
- [cli.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/cli.py:1)

### Storage / Analysis

- [schema.sql](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/db/schema.sql:1)
- [repository.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/db/repository.py:1)
- [cleaner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/normalize/cleaner.py:1)
- [evidence.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/normalize/evidence.py:1)
- [sql_guard.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/analysis/sql_guard.py:1)
- [trends.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/analysis/trends.py:1)

### Reporting / UI

- [builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:1)
- [app.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/ui/app.py:1)

## Verified Test Status

Last verified on `2026-04-27`:

```bash
pytest -q
```

Result:

```text
18 passed
```

## Current Behavior

### CLI

`search` currently:

- parses query
- initializes run plan
- prints parsed query info
- prints run stages
- prints trace events

### UI

Streamlit page currently:

- accepts a query
- parses it
- initializes SQLite at `data/insight.db`
- seeds sample `ChatGPT` and `Gemini` articles if missing
- loads matching articles by company
- shows:
  - parsed query
  - run plan
  - trace events
  - report preview
  - matching articles

## Current Limitation

The biggest current limitation is:

- [build_preview_report()](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:10) is still static
- it uses only `query_spec` and `run`
- it does not derive summary, findings, or evidence from actual SQLite article rows

## Single Next Recommended Step

Make `report preview` data-backed.

### Exact next implementation move

1. Update [test_report_builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_report_builder.py:1)
   - add a failing test where `build_preview_report(...)` accepts real article records

2. Update [builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:1)
   - generate summary from article count / company names / time range
   - generate findings from real article rows
   - generate evidence from article content or titles

3. Update [app.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/ui/app.py:1)
   - convert `matching_articles` into plain dicts
   - pass those records into `build_preview_report(...)`

## Verification Commands

For the next step:

```bash
pytest tests/test_report_builder.py -q
PYTHONPATH=src streamlit run src/insight_agent/ui/app.py
```

## Handoff Reference

For the latest detailed thread context, read:

- [2026-04-27-thread-memory.md](/Users/fangfei/Desktop/codex-fei/insight-agent/docs/superpowers/handoffs/2026-04-27-thread-memory.md:1)
