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

def test_build_preview_report_uses_bounded_evidence_snippet() -> None:
    long_content = (
        "OpenAI announced several updates before the main enterprise launch. "
        "The enterprise feature gives teams more control over deployment, "
        "governance, and internal adoption workflows."
    )

    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
            "companies": ["ChatGPT"],
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
                "title": "Enterprise launch",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": long_content,
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-enterprise-launch",
                "sentiment": "positive",
            }
        ],
    )

    snippet = payload["evidence"][0]

    assert "enterprise" in snippet["snippet_text"].lower()
    assert len(snippet["snippet_text"]) < len(long_content)
    assert snippet["snippet_start"] >= 0
    assert snippet["snippet_end"] > snippet["snippet_start"]

def test_build_preview_report_returns_evidence_for_each_company() -> None:
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
                "content": "OpenAI launched a new enterprise feature for ChatGPT teams.",
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
                "content": "Gemini announced a model update for developer workflows.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T11:00:00",
                "url": "https://example.com/gemini-update",
                "sentiment": "neutral",
            },
        ],
    )

    assert len(payload["evidence"]) == 2
    assert "ChatGPT" in payload["evidence"][0]["snippet_text"]
    assert "Gemini" in payload["evidence"][1]["snippet_text"]

def test_build_preview_report_attaches_evidence_source_metadata() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
            "companies": ["ChatGPT"],
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
                "content": "OpenAI launched a new enterprise feature for ChatGPT teams.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            }
        ],
    )

    evidence = payload["evidence"][0]

    assert evidence["company"] == "ChatGPT"
    assert evidence["title"] == "Launch update"
    assert evidence["source_name"] == "OpenAI"
    assert evidence["url"] == "https://example.com/openai-launch"

def test_build_preview_report_includes_sentiment_mix_finding() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        },
        {
            "plan": {
                "query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
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
                "content": "ChatGPT launched a new enterprise feature.",
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
                "content": "Gemini announced a model update.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T11:00:00",
                "url": "https://example.com/gemini-update",
                "sentiment": "neutral",
            },
        ],
    )

    assert "Sentiment mix: positive=1, neutral=1" in payload["findings"]

def test_build_preview_report_includes_trace_events() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
            "companies": ["ChatGPT"],
            "time_range": "30d",
            "metrics": ["sentiment"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        },
        {
            "plan": {
                "query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
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
                {"event_type": "run.started", "payload": {"query": "Compare ChatGPT"}},
                {"event_type": "run.plan_generated", "payload": {"stages": ["analysis"]}},
            ],
        },
        [
            {
                "company": "ChatGPT",
                "title": "Launch update",
                "source_name": "OpenAI",
                "source_type": "announcement",
                "content": "ChatGPT launched a new enterprise feature.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            }
        ],
    )

    assert payload["trace_events"][0]["event_type"] == "run.started"
    assert payload["trace_events"][1]["event_type"] == "run.plan_generated"

def test_build_preview_report_prefers_llm_analysis_when_provided() -> None:
    payload = build_preview_report(
        {
            "raw_query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        },
        {
            "plan": {
                "query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
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
                "content": "ChatGPT launched a new enterprise feature.",
                "published_date": "2026-04-20",
                "collected_at": "2026-04-20T10:00:00",
                "url": "https://example.com/openai-launch",
                "sentiment": "positive",
            }
        ],
        llm_analysis={
            "summary": "LLM summary: ChatGPT shows stronger product momentum.",
            "findings": ["LLM finding: ChatGPT has more enterprise-facing updates."],
            "risks": ["LLM risk: Evidence set is small."],
            "citations": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/openai-launch",
                }
            ],
        },
    )

    assert payload["summary"] == "LLM summary: ChatGPT shows stronger product momentum."
    assert payload["findings"][0] == "LLM finding: ChatGPT has more enterprise-facing updates."
    assert "LLM risk: Evidence set is small." in payload["findings"]
    assert payload["evidence"][0]["title"] == "Launch update"
    assert payload["evidence"][0]["url"] == "https://example.com/openai-launch"