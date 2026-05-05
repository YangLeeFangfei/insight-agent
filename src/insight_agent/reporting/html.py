from html import escape
from pathlib import Path


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

        evidence_items.append(
            f"""
            <article>
                <h3>{escape(company)}: {escape(title)}</h3>
                <p>{escape(snippet_text)}</p>
                <a href="{escape(url)}">{escape(source_name)}</a>
            </article>
            """
        )

    evidence_html = "".join(evidence_items)

    trace_events_html = "".join(
        f"<li>{escape(event['event_type'])}</li>"
        for event in payload.get("trace_events", [])
    )

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
