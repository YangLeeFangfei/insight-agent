import streamlit as st

from insight_agent.agent.harness import initialize_run
from insight_agent.agent.planner import parse_query
from insight_agent.reporting.builder import build_preview_report
from insight_agent.db.repository import init_db, insert_article, list_articles_for_companies
from pathlib import Path


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
        sample_articles = [
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
        ]

        for article in sample_articles:
            insert_article(db_path, article)
        
    matching_articles = list_articles_for_companies(db_path, query_spec["companies"])
    article_records = [dict(row) for row in matching_articles]

    run = initialize_run(query_spec)
    report = build_preview_report(query_spec, run, article_records)

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

        st.write("Findings:")
        for finding in report["findings"]:
            st.write(f"- {finding}")

        st.write("Evidence:")
        for item in report["evidence"]:
            st.write(f"- {item['snippet_text']}")

        st.subheader("Matching Articles")
        for row in matching_articles:
            st.write(f"- {row['company']}: {row['title']}")
    
else:
    st.subheader("Current Status")
    st.write("UI scaffold is ready.")

    st.subheader("Query Preview")
    st.code(query)
