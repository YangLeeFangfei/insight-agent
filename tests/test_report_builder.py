from insight_agent.reporting.builder import build_report_payload
from insight_agent.reporting.builder import build_preview_report

def test_build_report_payload_returns_structured_payload() -> None:
    payload = build_report_payload(
        summary="ChatGPT and Gemini both increased discussion volume.",
        findings=[
            "ChatGPT had stronger positive sentiment.",
            "Gemini showed more topic diversity.",
        ],
        evidence=[
            {
                "snippet_text": "OpenAI launched a new feature for enterprise teams.",
                "snippet_start": 0,
                "snippet_end": 42,
            }
        ],
    )

    assert payload["summary"] == "ChatGPT and Gemini both increased discussion volume."
    assert payload["findings"][0] == "ChatGPT had stronger positive sentiment."
    assert payload["evidence"][0]["snippet_text"].startswith("OpenAI launched")


def test_build_preview_report_returns_ui_ready_payload() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment", "topics"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        },
        {
            "plan": {
                "query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
                "needs_confirmation": True,
                "stages": [
                    "plan_preview",
                    "source_collection",
                    "normalization",
                    "analysis",
                    "evidence_binding",
                    "reporting",
                ],
            },
            "events": [
                {"event_type": "run.started", "payload": {}},
                {"event_type": "run.plan_generated", "payload": {}},
            ],
        },
    )

    assert "ChatGPT" in payload["summary"]
    assert "Gemini" in payload["summary"]
    assert payload["findings"][0].startswith("Metrics:")
    assert payload["evidence"][0]["snippet_text"].startswith("Planned sources:")


def test_build_preview_report_uses_article_records() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment", "topics"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        },
        {
            "plan": {
                "query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
                "needs_confirmation": True,
                "stages": [
                    "plan_preview",
                    "source_collection",
                    "normalization",
                    "analysis",
                    "evidence_binding",
                    "reporting",
                ],
            },
            "events": [
                {"event_type": "run.started", "payload": {}},
                {"event_type": "run.plan_generated", "payload": {}},
            ],
        },
        [
            {
                "company": "ChatGPT",
                "title": "Launch update",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": "OpenAI launched a new feature for enterprise teams.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            },
            {
                "company": "Gemini",
                "title": "Model update",
                "source_name": "Google",
                "source_type": "announcement",
                "content": "Gemini announced a model update for developers.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T11:00:00",
                "url": "https://example.com/gemini-update",
                "sentiment": "neutral",
            },
        ],
    )

    assert "2 articles" in payload["summary"]
    assert payload["findings"][0].startswith("Companies covered:")
    assert payload["evidence"][0]["snippet_text"].startswith("OpenAI launched")