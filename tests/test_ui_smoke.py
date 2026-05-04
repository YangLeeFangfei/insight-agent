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

    assert 'use_llm = st.checkbox("Use LLM analysis")' in app_source
    assert "analyze_articles" in app_source
    assert "build_llm_client" in app_source
    assert "llm_analysis=llm_analysis" in app_source

def test_streamlit_app_renders_evidence_with_optional_metadata() -> None:
    app_source = Path("src/insight_agent/ui/app.py").read_text()

    assert 'item.get("company", "Unknown company")' in app_source
    assert 'item.get("source_name", "Unknown source")' in app_source
    assert 'item.get("title", "Untitled evidence")' in app_source
    assert 'item.get("url", "")' in app_source
