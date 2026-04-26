from pathlib import Path


def test_streamlit_app_file_exists() -> None:
    app_path = Path("src/insight_agent/ui/app.py")

    assert app_path.exists()
