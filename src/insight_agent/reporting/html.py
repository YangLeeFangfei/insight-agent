import json
from html import escape
from pathlib import Path

from insight_agent.reporting.evidence_quality import normalize_evidence_summary


def _safe_link_url(url: object) -> str:
    url_text = str(url)
    if url_text.startswith(("https://", "http://")):
        return url_text

    return "#"


def render_html_report(payload: dict[str, object]) -> str:
    findings_html = "".join(
        f"<li>{escape(finding)}</li>"
        for finding in payload["findings"]
    )

    evidence_items = []
    for item in payload["evidence"]:
        company = item.get("company", "Unknown company")
        title = item.get("title", "Untitled evidence")
        snippet_text = item.get("snippet_text", "")
        url = item.get("url", "")
        source_name = item.get("source_name", "Unknown source")
        safe_url = _safe_link_url(url)

        evidence_items.append(
            f"""
            <article>
                <h3>{escape(company)}: {escape(title)}</h3>
                <p>{escape(snippet_text)}</p>
                <a href="{escape(safe_url)}">{escape(source_name)}</a>
            </article>
            """
        )

    evidence_html = "".join(evidence_items)

    evidence_summary = payload.get("evidence_summary")
    evidence_summary_html = ""
    if evidence_summary is not None:
        evidence_quality = normalize_evidence_summary(evidence_summary)
        grounded_citations = escape(str(evidence_quality["grounded_citations"]))
        ungrounded_citations = escape(str(evidence_quality["ungrounded_citations"]))
        duplicate_citations = escape(str(evidence_quality["duplicate_citations"]))
        evidence_summary_html = f"""
            <section>
                <h2>Evidence Quality</h2>
                <ul>
                    <li>Grounded citations: {grounded_citations}</li>
                    <li>Ungrounded citations: {ungrounded_citations}</li>
                    <li>Duplicate citations: {duplicate_citations}</li>
                </ul>
            </section>
        """

    trace_event_items = []
    for event in payload.get("trace_events", []):
        event_payload = json.dumps(
            event.get("payload", {}),
            sort_keys=True,
        )
        trace_event_items.append(
            f"""
            <li>
                <strong>{escape(event["event_type"])}</strong>
                <pre>{escape(event_payload)}</pre>
            </li>
            """
        )

    trace_events_html = "".join(trace_event_items)

    return f"""
    <html>
        <body>
            <h1>Insight Agent Report</h1>
            <section>
                <h2>Summary</h2>
                <p>{escape(payload["summary"])}</p>
            </section>
            <section>
                <h2>Findings</h2>
                <ul>{findings_html}</ul>
            </section>
            <section>
                <h2>Evidence</h2>
                {evidence_html}
            </section>
            {evidence_summary_html}
            <section>
                <h2>Trace Events</h2>
                <ul>{trace_events_html}</ul>
            </section>
        </body>
    </html>
    """


def write_html_report(
    payload: dict[str, object],
    output_path: Path,
) -> Path:
    html = render_html_report(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    return output_path
