from insight_agent.config import (
    get_collector_mode,
    get_news_api_key,
    get_llm_api_key,
    get_llm_model,
    get_llm_base_url,
)

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

def test_get_llm_api_key_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-llm-key")

    assert get_llm_api_key() == "test-llm-key"


def test_get_llm_api_key_returns_none_when_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    assert get_llm_api_key() is None


def test_get_llm_model_defaults_to_mimo_v2_5_pro(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert get_llm_model() == "mimo-v2.5-pro"


def test_get_llm_model_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")

    assert get_llm_model() == "mimo-v2.5"


def test_get_llm_base_url_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    assert get_llm_base_url() == "https://token-plan-cn.xiaomimimo.com/v1"


