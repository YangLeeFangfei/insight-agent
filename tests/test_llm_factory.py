from insight_agent.llm.client import OpenAICompatibleLLMClient
from insight_agent.llm.factory import FakeLLMClient, build_llm_client


def test_build_llm_client_returns_fake_client_without_api_key(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    client = build_llm_client()

    assert isinstance(client, FakeLLMClient)


def test_build_llm_client_returns_openai_compatible_client_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-llm-key")
    monkeypatch.setenv("LLM_MODEL", "mimo-v2.5")
    monkeypatch.setenv("LLM_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    client = build_llm_client()

    assert isinstance(client, OpenAICompatibleLLMClient)
    assert client.model == "mimo-v2.5"
