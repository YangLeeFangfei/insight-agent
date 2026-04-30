from pathlib import Path

import streamlit as st

from insight_agent.agent.harness import initialize_run
from insight_agent.agent.planner import parse_query
from insight_agent.db.repository import init_db, insert_article, list_articles_for_companies
from insight_agent.reporting.builder import build_preview_report
from insight_agent.reporting.html import write_html_report
from insight_agent.collectors.demo import collect_demo_articles


st.set_page_config(page_title="Insight Agent", layout="wide")
st.title("Insight Agent")
st.caption("Workflow-first competitive intelligence workbench")

query = st.text_area(
    "Query",
    "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
)

if st.button("Preview Run"):
    query_spec = parse_query(query)

    db_path = Path("data/insight.db")
    init_db(db_path)

    existing_rows = list_articles_for_companies(db_path, query_spec["companies"])

    if not existing_rows:
        for article in collect_demo_articles(query_spec["companies"]):
            insert_article(db_path, article)

    matching_articles = list_articles_for_companies(db_path, query_spec["companies"])
    article_records = [dict(row) for row in matching_articles]

    run = initialize_run(query_spec)
    report = build_preview_report(query_spec, run, article_records)
    report_path = write_html_report(
        report,
        Path("data/reports/preview-report.html"),
    )

    left_col, right_col = st.columns([1, 1])

    with left_col:

        st.subheader("Parsed Query")
        st.write(f"Companies: {', '.join(query_spec['companies'])}")
        st.write(f"Time range: {query_spec['time_range']}")
        st.write(f"Metrics: {', '.join(query_spec['metrics'])}")
        st.write(
            f"Source types: {', '.join(query_spec['plan_preview']['source_types'])}"
        )
        st.subheader("Run Plan")
        st.write(f"Needs confirmation: {run['plan']['needs_confirmation']}")
        st.write(f"Stages: {', '.join(run['plan']['stages'])}")

    with right_col:

        st.subheader("Trace Events")
        for event in run["events"]:
            st.write(f"- {event['event_type']}")

        st.subheader("Report Preview")
        st.write(f"Summary: {report['summary']}")
        st.write(f"HTML report: {report_path}")
        html_report = report_path.read_text()

        st.download_button(
            "Download HTML report",
            data=html_report,
            file_name="preview-report.html",
            mime="text/html",
        )

        st.write("Findings:")
        for finding in report["findings"]:
            st.write(f"- {finding}")

        st.write("Evidence:")
        for item in report["evidence"]:
            st.write(f"- {item['company']} / {item['source_name']}: {item['title']}")
            st.write(item["snippet_text"])
            st.write(item["url"])

        st.subheader("Matching Articles")
        for row in matching_articles:
            st.write(f"- {row['company']}: {row['title']}")

else:
    st.subheader("Current Status")
    st.write("UI scaffold is ready.")

    st.subheader("Query Preview")
    st.code(query)
