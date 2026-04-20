# Insight Agent

Insight Agent is an AI-assisted competitive intelligence workspace. This repository currently contains the Day 1 project skeleton: Python package layout, CLI entry point, environment template, and initial tests.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m insight_agent.cli --help
```

## Initial Scope

- CLI-first MVP
- SQLite for local persistence
- Source collectors for news, announcements, and industry content
- Structured analysis outputs for volume, sentiment, and topics
- HTML reports with evidence citations

