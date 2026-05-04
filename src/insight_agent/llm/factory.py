from insight_agent.llm.client import OpenAICompatibleLLMClient
from insight_agent.config import get_llm_api_key, get_llm_model, get_llm_base_url

class FakeLLMClient:
    def complete(self, prompt: str) -> str:
        return """
        {
            "summary": "LLM summary: ChatGPT shows stronger product momentum.",
            "findings": ["LLM finding: ChatGPT has more enterprise-facing updates."],
            "risks": ["LLM risk: Evidence set is small."],
            "citations": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/openai-launch"
                }
            ]
        }
        """
    
def build_llm_client():
    api_key = get_llm_api_key()

    if api_key is None:
        return FakeLLMClient()

    return OpenAICompatibleLLMClient(
        api_key=api_key,
        model=get_llm_model(),
        base_url=get_llm_base_url(),
    )
