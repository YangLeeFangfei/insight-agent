# Insight Agent Thread Memory

## Purpose

This file is a detailed handoff summary for a new Codex session.

Use it when:

- a session is being switched
- a new thread needs the last thread's local reasoning
- `CURRENT_STATE.md` is not enough and more detailed context is needed

For the short always-current status board, read:

- [CURRENT_STATE.md](/Users/fangfei/Desktop/codex-fei/insight-agent/docs/superpowers/handoffs/CURRENT_STATE.md:1)

## Project Context

- Repo: `/Users/fangfei/Desktop/codex-fei/insight-agent`
- GitHub: [YangLeeFangfei/insight-agent](https://github.com/YangLeeFangfei/insight-agent)
- Main design spec:
  - [2026-04-20-insight-agent-final-design.md](/Users/fangfei/Desktop/codex-fei/insight-agent/docs/superpowers/specs/2026-04-20-insight-agent-final-design.md:1)
- Main implementation plan:
  - [2026-04-20-insight-agent-final-implementation-plan.md](/Users/fangfei/Desktop/codex-fei/insight-agent/docs/superpowers/plans/2026-04-20-insight-agent-final-implementation-plan.md:1)

## Collaboration Style

The user wants a coach-style workflow:

- Do not auto-generate the whole project unless explicitly asked.
- Explain each step in terms of:
  - current phase
  - current artifact
  - why this step matters
  - exact next change
- Keep guidance tied to the main track, not scattered syntax trivia.

## Main Track

The project has been built along these phases:

1. `Query -> Plan`
2. `Data -> SQLite`
3. `Normalize -> Evidence`
4. `Analysis -> Trends`
5. `Harness -> Report`
6. `CLI / Web UI`

## Completed Phases

### Phase 1: Query -> Plan

Implemented:

- [planner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/planner.py:1)
- [cli.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/cli.py:1)
- [test_planner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_planner.py:1)

Current `parse_query()` returns:

- `raw_query`
- `companies`
- `time_range`
- `metrics`
- `plan_preview`

### Phase 2: Data -> SQLite

Implemented:

- [schema.sql](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/db/schema.sql:1)
- [repository.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/db/repository.py:1)
- [test_repository.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_repository.py:1)

Current repository functions:

- `_connect`
- `init_db`
- `insert_article`
- `list_articles`
- `list_articles_for_companies`

### Phase 3: Normalize -> Evidence

Implemented:

- [cleaner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/normalize/cleaner.py:1)
- [evidence.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/normalize/evidence.py:1)
- [test_enricher.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_enricher.py:1)

Current functions:

- `normalize_article`
- `build_evidence_snippet`

### Phase 4: Analysis -> Trends

Implemented:

- [sql_guard.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/analysis/sql_guard.py:1)
- [trends.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/analysis/trends.py:1)
- [test_sql_guard.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_sql_guard.py:1)
- [test_trends.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_trends.py:1)

Current functions:

- `validate_read_only_sql`
- `detect_volume_spike`

### Phase 5: Harness -> Report

Implemented:

- [harness.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/harness.py:1)
- [trace.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/trace.py:1)
- [builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:1)
- [test_harness.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_harness.py:1)
- [test_trace.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_trace.py:1)
- [test_report_builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_report_builder.py:1)

Current functions:

- `build_run_plan`
- `initialize_run`
- `build_trace_event`
- `build_report_payload`
- `build_preview_report`

Important note:

- `build_preview_report()` is still static.
- It uses `query_spec` and `run`, but not actual DB article content yet.
- This is the main next improvement area.

### Phase 6: CLI / Web UI

Implemented:

- CLI entry in [cli.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/cli.py:1)
- Streamlit UI in [app.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/ui/app.py:1)
- UI smoke test in [test_ui_smoke.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_ui_smoke.py:1)

Current UI behavior:

- Streamlit page loads successfully.
- Query input exists.
- Clicking `Preview Run` does:
  - `parse_query(query)`
  - `init_db(Path("data/insight.db"))`
  - seed sample articles if matching company rows do not exist
  - `list_articles_for_companies(...)`
  - `initialize_run(query_spec)`
  - `build_preview_report(query_spec, run)`
- UI shows:
  - parsed query
  - run plan
  - trace events
  - report preview
  - matching articles

## Current Key Files

- [src/insight_agent/agent/planner.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/planner.py:1)
- [src/insight_agent/agent/harness.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/harness.py:1)
- [src/insight_agent/agent/trace.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/agent/trace.py:1)
- [src/insight_agent/db/repository.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/db/repository.py:1)
- [src/insight_agent/reporting/builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:1)
- [src/insight_agent/ui/app.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/ui/app.py:1)

## Verified Test Status

Verified on 2026-04-27:

```bash
pytest -q
```

Result:

```text
18 passed in 0.05s
```

## Current Limitation

The biggest current limitation is:

- report preview is still generated from static strings
- it does not yet summarize or derive findings from actual `matching_articles`
- evidence in the report preview is not yet based on stored article content

## Recommended Next Step

### Goal

Make `report preview` data-backed instead of static.

### Recommended implementation direction

1. Update [test_report_builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/tests/test_report_builder.py:1)
   - add a failing test for a DB-backed preview report function
   - likely pass article records into `build_preview_report(...)`

2. Update [builder.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/reporting/builder.py:1)
   - change `build_preview_report()` so it can use actual article rows
   - generate:
     - summary from real companies / article count / time range
     - findings from real rows
     - evidence from real article content or titles

3. Update [app.py](/Users/fangfei/Desktop/codex-fei/insight-agent/src/insight_agent/ui/app.py:1)
   - convert `matching_articles` into plain dicts if needed:
     - `article_records = [dict(row) for row in matching_articles]`
   - pass those into `build_preview_report(...)`

4. Re-run:

```bash
pytest tests/test_report_builder.py -q
```

Then manually verify:

```bash
PYTHONPATH=src streamlit run src/insight_agent/ui/app.py
```

### Suggested coach-style framing for the next session

If continuing in a new session, use this framing:

- Current phase: `Harness -> Report` moving toward `data-backed report preview`
- Current artifact: `report builder` + `UI integration`
- Immediate goal: make `Report Preview` depend on SQLite article rows instead of static strings

## Suggested Prompt For A New Session

Use this in the new session:

```text
请先读取 /Users/fangfei/Desktop/codex-fei/insight-agent/docs/superpowers/handoffs/2026-04-27-thread-memory.md，然后继续带我做下一步：让 report preview 开始基于数据库内容生成，而不是纯静态字符串。保持教练模式，一次只带我做一小步。
```
