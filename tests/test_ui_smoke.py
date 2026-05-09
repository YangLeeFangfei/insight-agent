from pathlib import Path


def test_streamlit_app_file_exists() -> None:
    app_path = Path("src/insight_agent/ui/app.py")

    assert app_path.exists()

def test_streamlit_app_supports_force_refresh() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert 'force_refresh = st.checkbox("Force refresh")' in app_source
    assert "refresh=force_refresh" in app_source

def test_streamlit_app_uses_ingestion_pipeline() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "load_or_collect_articles" in app_source
    assert "collect_fn=collect_articles" in app_source

def test_streamlit_app_reads_ingestion_result_metadata() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "ingestion_result = load_or_collect_articles" in app_source
    assert "article_records = ingestion_result.articles" in app_source
    assert "ingestion_result.used_cache" in app_source
    assert "ingestion_result.collected_count" in app_source

def test_streamlit_app_supports_llm_analysis_toggle() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert 'use_llm = st.checkbox("Use LLM analysis", value=True)' in app_source
    assert "analyze_articles" in app_source
    assert "build_llm_client" in app_source
    assert "llm_analysis=llm_analysis" in app_source

def test_streamlit_app_renders_evidence_with_optional_metadata() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert 'item.get("company", "Unknown company")' in app_source
    assert 'item.get("source_name", "Unknown source")' in app_source
    assert 'item.get("title", "Untitled evidence")' in app_source
    assert 'item.get("url", "")' in app_source

def test_streamlit_app_displays_run_status() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "st.write(f\"Status: {run['status']}\")" in app_source


def test_streamlit_app_displays_run_id() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "st.write(f\"Run ID: {run['run_id']}\")" in app_source


def test_streamlit_app_persists_run_status_updates() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "from insight_agent.db.repository import get_run, list_runs, save_run" in app_source
    assert app_source.count("save_run(db_path, run)") >= 3


def test_streamlit_app_displays_run_history() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "list_runs" in app_source
    assert 'st.subheader("Run History")' in app_source
    assert 'history_limit = st.number_input("History limit"' in app_source
    assert 'history_status = st.selectbox("History status"' in app_source
    assert 'history_status_filter = None if history_status == "all" else history_status' in app_source
    assert (
        "saved_runs = list_runs("
        in app_source
    )
    assert "status=history_status_filter" in app_source
    assert "for saved_run in saved_runs" in app_source


def test_streamlit_app_displays_empty_run_history_state() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "if not saved_runs:" in app_source
    assert 'st.write("No saved runs.")' in app_source


def test_streamlit_app_displays_run_detail_lookup() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "import json" in app_source
    assert "from insight_agent.db.repository import get_run, list_runs, save_run" in app_source
    assert 'st.subheader("Run Detail")' in app_source
    assert 'default_run_id = saved_runs[0]["run_id"] if saved_runs else ""' in app_source
    assert 'run_id_lookup = st.text_input("Run ID", value=default_run_id)' in app_source
    assert 'if st.button("Load Run"):' in app_source
    assert "selected_run = get_run(db_path, run_id_lookup)" in app_source
    assert 'st.write("Run not found.")' in app_source
    assert "st.write(f\"Run status: {selected_run['status']}\")" in app_source
    assert "for event in selected_run[\"events\"]" in app_source
    assert 'event_payload = json.dumps(event.get("payload", {}), sort_keys=True)' in app_source
    assert "st.write(f\"- {event['event_type']}: {event_payload}\")" in app_source


def test_streamlit_app_records_analysis_completed_status() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "record_analysis_completed" in app_source
    assert "run = record_analysis_completed(run, llm_analysis)" in app_source


def test_streamlit_app_records_report_completed_status() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "record_report_completed" in app_source
    assert "run = record_report_completed(run, report)" in app_source


def test_streamlit_app_syncs_report_trace_events_after_report_completed() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert 'report["trace_events"] = run["events"]' in app_source


def test_streamlit_app_records_failed_status_when_llm_analysis_fails() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert "record_run_failed" in app_source
    assert "run = record_run_failed(run, \"analysis\", str(exc))" in app_source
    assert 'st.error(f"LLM analysis failed: {exc}")' in app_source
