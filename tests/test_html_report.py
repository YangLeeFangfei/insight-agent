
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
