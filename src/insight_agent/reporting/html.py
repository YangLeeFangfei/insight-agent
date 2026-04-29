from html import escape
from pathlib import Path


def render_html_report(payload: dict[str, object]) -> str:
    findings_html = "".join(
        f"<li>{escape(finding)}</li>"
        for finding in payload["findings"]
    )

    evidence_html = "".join(
        f"""
        <article>
            <h3>{escape(item["company"])}: {escape(item["title"])}</h3>
            <p>{escape(item["snippet_text"])}</p>
            <a href="{escape(item["url"])}">{escape(item["source_name"])}</a>
        </article>
        """
        for item in payload["evidence"]
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
