import json
from pathlib import Path

import streamlit as st

from insight_agent.agent.planner import parse_query
from insight_agent.reporting.builder import build_preview_report
from insight_agent.reporting.html import write_html_report
from insight_agent.collectors.selector import collect_articles
from insight_agent.collectors.base import build_collection_request
from insight_agent.db.repository import get_run, list_runs, save_run
from insight_agent.ingestion import load_or_collect_articles
from insight_agent.llm.analyst import analyze_articles
from insight_agent.llm.factory import build_llm_client
from insight_agent.reporting.evidence_quality import normalize_evidence_summary
from insight_agent.agent.harness import (
    initialize_run,
    record_collection_completed,
    record_analysis_completed,
    record_report_completed,
    record_run_failed,
)


st.set_page_config(page_title="Insight Agent", layout="wide")
st.title("Insight Agent")
st.caption("Workflow-first competitive intelligence workbench")
db_path = Path("data/insight.db")

query = st.text_area(
    "Query",
    "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
)
force_refresh = st.checkbox("Force refresh")
use_llm = st.checkbox("Use LLM analysis", value=True)

if st.button("Preview Run"):
    query_spec = parse_query(query)
    collection_request = build_collection_request(query_spec)

    ingestion_result = load_or_collect_articles(
        db_path=db_path,
        companies=query_spec["companies"],
        collection_request=collection_request,
        collect_fn=collect_articles,
        refresh=force_refresh,
    )
    article_records = ingestion_result.articles
    run = initialize_run(query_spec, collection_request)
    run = record_collection_completed(run, article_records)
    save_run(db_path, run)
    llm_analysis = None
    llm_failed = False
    if use_llm:
        try:
            llm_analysis = analyze_articles(
                query_spec=query_spec,
                articles=article_records,
                client=build_llm_client(),
            )
        except Exception as exc:
            run = record_run_failed(run, "analysis", str(exc))
            save_run(db_path, run)
            st.error(f"LLM analysis failed: {exc}")
            llm_failed = True

        if not llm_failed:
            run = record_analysis_completed(run, llm_analysis)
            save_run(db_path, run)


    report = None
    report_path = None
    if not llm_failed:
        report = build_preview_report(
            query_spec,
            run,
            article_records,
            llm_analysis=llm_analysis,
        )
        run = record_report_completed(run, report)
        save_run(db_path, run)
        report["trace_events"] = run["events"]
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
        st.write(f"Run ID: {run['run_id']}")
        st.write(f"Status: {run['status']}")
        st.subheader("Ingestion")
        st.write(f"Used cache: {ingestion_result.used_cache}")
        st.write(f"Collected: {ingestion_result.collected_count}")
        st.write(f"Articles: {len(article_records)}")


    with right_col:

        st.subheader("Trace Events")
        for event in run["events"]:
            st.write(f"- {event['event_type']}")

        if report is not None and report_path is not None:
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

            evidence_summary = report.get("evidence_summary")
            if evidence_summary is not None:
                evidence_quality = normalize_evidence_summary(evidence_summary)
                st.write("Evidence quality:")
                st.write(
                    f"- Grounded citations: {evidence_quality['grounded_citations']}"
                )
                st.write(
                    f"- Ungrounded citations: {evidence_quality['ungrounded_citations']}"
                )
                st.write(
                    f"- Duplicate citations: {evidence_quality['duplicate_citations']}"
                )

            st.write("Evidence:")
            for item in report["evidence"]:
                company = item.get("company", "Unknown company")
                source_name = item.get("source_name", "Unknown source")
                title = item.get("title", "Untitled evidence")
                url = item.get("url", "")
                snippet_text = item.get("snippet_text", "")

                st.write(f"- {company} / {source_name}: {title}")
                st.write(snippet_text)
                st.write(url)

        st.subheader("Matching Articles")
        for row in article_records:
            st.write(f"- {row['company']}: {row['title']}")

else:
    st.subheader("Current Status")
    st.write("UI scaffold is ready.")

    st.subheader("Query Preview")
    st.code(query)

st.subheader("Run History")
history_limit = st.number_input("History limit", min_value=1, value=10, step=1)
history_status = st.selectbox("History status", ["all", "report_completed", "failed"])
history_status_filter = None if history_status == "all" else history_status
saved_runs = list_runs(
    db_path,
    limit=history_limit,
    status=history_status_filter,
)
if not saved_runs:
    st.write("No saved runs.")
else:
    for saved_run in saved_runs:
        st.write(
            f"- {saved_run['run_id']} | {saved_run['status']} | {saved_run['updated_at']} | {saved_run['query']}"
        )

st.subheader("Run Detail")
default_run_id = saved_runs[0]["run_id"] if saved_runs else ""
run_id_lookup = st.text_input("Run ID", value=default_run_id)
if st.button("Load Run"):
    selected_run = get_run(db_path, run_id_lookup)
    if selected_run is None:
        st.write("Run not found.")
    else:
        st.write(f"Run status: {selected_run['status']}")
        st.write(f"Updated at: {selected_run['updated_at']}")
        st.write("Saved trace events:")
        for event in selected_run["events"]:
            event_payload = json.dumps(event.get("payload", {}), sort_keys=True)
            st.write(f"- {event['event_type']}: {event_payload}")
