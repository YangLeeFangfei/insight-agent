from insight_agent.config import get_collector_mode, get_news_api_key


def test_get_news_api_key_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("NEWS_API_KEY", "test-news-key")

    assert get_news_api_key() == "test-news-key"


def test_get_news_api_key_returns_none_when_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    assert get_news_api_key() is None

def test_get_collector_mode_defaults_to_demo(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INSIGHT_COLLECTOR", raising=False)

    assert get_collector_mode() == "demo"

def test_get_collector_mode_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("INSIGHT_COLLECTOR", "news")

    assert get_collector_mode() == "news"

def test_get_news_api_key_reads_dotenv_file(monkeypatch, tmp_path) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("NEWS_API_KEY=dotenv-news-key\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    assert get_news_api_key() == "dotenv-news-key"
