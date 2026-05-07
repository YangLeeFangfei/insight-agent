
from pathlib import Path
from insight_agent.reporting.html import render_html_report, write_html_report


def test_render_html_report_includes_summary_findings_and_evidence() -> None:
    html = render_html_report(
        {
            "summary": "Prepared analysis run for ChatGPT and Gemini.",
            "findings": [
                "Companies covered: ChatGPT, Gemini",
                "Sentiment mix: positive=1, neutral=1",
            ],
            "evidence": [
                {
                    "company": "ChatGPT",
                    "title": "Launch update",
                    "source_name": "OpenAI",
                    "url": "https://example.com/openai-launch",
                    "snippet_text": "ChatGPT launched a new enterprise feature.",
                    "snippet_start": 0,
                    "snippet_end": 42,
                }
            ],
        }
    )

    assert "<html" in html
    assert "Prepared analysis run" in html
    assert "Sentiment mix: positive=1, neutral=1" in html
    assert "ChatGPT launched a new enterprise feature." in html
    assert "https://example.com/openai-launch" in html

def test_write_html_report_writes_file(tmp_path) -> None:
    output_path = tmp_path / "reports" / "preview-report.html"

    written_path = write_html_report(
        {
            "summary": "Prepared analysis run for ChatGPT.",
            "findings": ["Sentiment mix: positive=1"],
            "evidence": [
                {
                    "company": "ChatGPT",
                    "title": "Launch update",
                    "source_name": "OpenAI",
                    "url": "https://example.com/openai-launch",
                    "snippet_text": "ChatGPT launched a new enterprise feature.",
                    "snippet_start": 0,
                    "snippet_end": 42,
                }
            ],
        },
        output_path,
    )

    assert written_path == output_path
    assert output_path.exists()
    assert "Prepared analysis run for ChatGPT." in output_path.read_text()

def test_render_html_report_escapes_payload_content() -> None:
    html = render_html_report(
        {
            "summary": "<script>alert('summary')</script>",
            "findings": ["<b>dangerous finding</b>"],
            "evidence": [
                {
                    "company": "ChatGPT",
                    "title": "<script>alert('title')</script>",
                    "source_name": "OpenAI",
                    "url": "https://example.com/openai-launch",
                    "snippet_text": "<img src=x onerror=alert(1)>",
                    "snippet_start": 0,
                    "snippet_end": 28,
                }
            ],
        }
    )

    assert "<script>" not in html
    assert "<b>dangerous finding</b>" not in html
    assert "<img src=x onerror=alert(1)>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;dangerous finding&lt;/b&gt;" in html

def test_render_html_report_includes_trace_events() -> None:
    html = render_html_report(
        {
            "summary": "Prepared analysis run for ChatGPT.",
            "findings": ["Sentiment mix: positive=1"],
            "evidence": [
                {
                    "company": "ChatGPT",
                    "title": "Launch update",
                    "source_name": "OpenAI",
                    "url": "https://example.com/openai-launch",
                    "snippet_text": "ChatGPT launched a new enterprise feature.",
                    "snippet_start": 0,
                    "snippet_end": 42,
                }
            ],
            "trace_events": [
                {"event_type": "run.started", "payload": {"query": "Compare ChatGPT"}},
                {"event_type": "run.plan_generated", "payload": {"stages": ["analysis"]}},
                {
                    "event_type": "run.report_completed",
                    "payload": {
                        "grounded_citation_count": 2,
                        "ungrounded_citation_count": 1,
                        "duplicate_citation_count": 0,
                    },
                },
            ],
        }
    )

    assert "Trace Events" in html
    assert "run.started" in html
    assert "run.plan_generated" in html
    assert "run.report_completed" in html
    assert "grounded_citation_count" in html
    assert "2" in html


def test_render_html_report_escapes_trace_event_payload() -> None:
    html = render_html_report(
        {
            "summary": "Prepared analysis run.",
            "findings": ["Finding."],
            "evidence": [],
            "trace_events": [
                {
                    "event_type": "run.failed",
                    "payload": {
                        "error_message": "<script>alert('trace')</script>",
                    },
                },
            ],
        }
    )

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_render_html_report_handles_llm_citation_evidence() -> None:
    html = render_html_report(
        {
            "summary": "LLM summary.",
            "findings": ["LLM finding."],
            "evidence": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/openai-launch",
                    "snippet_text": "Launch update",
                    "snippet_start": 0,
                    "snippet_end": 13,
                }
            ],
        }
    )

    assert "Unknown company" in html
    assert "Unknown source" in html
    assert "Launch update" in html
    assert "https://example.com/openai-launch" in html


def test_render_html_report_includes_evidence_quality_summary() -> None:
    html = render_html_report(
        {
            "summary": "LLM summary.",
            "findings": ["LLM finding."],
            "evidence": [],
            "evidence_summary": {
                "grounded_citations": 2,
                "ungrounded_citations": 1,
                "duplicate_citations": 3,
            },
        }
    )

    assert "Evidence Quality" in html
    assert "Grounded citations: 2" in html
    assert "Ungrounded citations: 1" in html
    assert "Duplicate citations: 3" in html


def test_render_html_report_defaults_missing_evidence_quality_counts() -> None:
    html = render_html_report(
        {
            "summary": "LLM summary.",
            "findings": ["LLM finding."],
            "evidence": [],
            "evidence_summary": {
                "grounded_citations": 2,
            },
        }
    )

    assert "Grounded citations: 2" in html
    assert "Ungrounded citations: 0" in html
    assert "Duplicate citations: 0" in html


def test_render_html_report_escapes_evidence_quality_summary() -> None:
    html = render_html_report(
        {
            "summary": "LLM summary.",
            "findings": ["LLM finding."],
            "evidence": [],
            "evidence_summary": {
                "grounded_citations": "<script>alert('grounded')</script>",
                "ungrounded_citations": 1,
                "duplicate_citations": 0,
            },
        }
    )

    assert "<script>" not in html
    assert "Grounded citations: 0" in html


def test_render_html_report_blocks_unsafe_evidence_urls() -> None:
    html = render_html_report(
        {
            "summary": "Prepared analysis run.",
            "findings": ["Finding."],
            "evidence": [
                {
                    "company": "ChatGPT",
                    "title": "Unsafe source",
                    "source_name": "Unknown",
                    "url": "javascript:alert(1)",
                    "snippet_text": "Unsafe URL should not be linked.",
                    "snippet_start": 0,
                    "snippet_end": 32,
                }
            ],
        }
    )

    assert 'href="javascript:alert(1)"' not in html
    assert 'href="#"' in html
