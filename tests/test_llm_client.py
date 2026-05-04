from insight_agent.llm.client import OpenAICompatibleLLMClient


class FakeMessage:
    content = "model output"


class FakeChoice:
    message = FakeMessage()


class FakeChatCompletionResponse:
    choices = [FakeChoice()]

class FakeCompletions:
    def __init__(self) -> None:
        self.calls = []

    def create(self, model: str, messages: list[dict[str, str]]):
        self.calls.append(
            {
                "model": model,
                "messages": messages,
            }
        )
        return FakeChatCompletionResponse()


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeCompletions()


class FakeSDKClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


def test_openai_compatible_llm_client_uses_chat_completions_api() -> None:
    sdk_client = FakeSDKClient()
    client = OpenAICompatibleLLMClient(
        api_key="test-llm-key",
        model="mimo-v2.5",
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
        sdk_client=sdk_client,
    )

    output = client.complete("Analyze these articles.")

    assert output == "model output"
    assert sdk_client.chat.completions.calls == [
        {
            "model": "mimo-v2.5",
            "messages": [
                {"role": "user", "content": "Analyze these articles."},
            ],
        }
    ]
