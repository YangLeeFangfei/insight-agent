import streamlit as st

from insight_agent.agent.harness import initialize_run
from insight_agent.agent.planner import parse_query


st.set_page_config(page_title="Insight Agent", layout="wide")
st.title("Insight Agent")
st.caption("Workflow-first competitive intelligence workbench")

query = st.text_area(
    "Query",
    "Compare ChatGPT and Gemini sentiment and topics in the last 30 days",
)

if st.button("Preview Run"):
    query_spec = parse_query(query)
    run = initialize_run(query_spec)

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

    st.subheader("Trace Events")
    for event in run["events"]:
        st.write(f"- {event['event_type']}")
else:
    st.subheader("Current Status")
    st.write("UI scaffold is ready.")

    st.subheader("Query Preview")
    st.code(query)
