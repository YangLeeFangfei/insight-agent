from insight_agent.llm.analyst import analyze_articles


class FakeLLMClient:
    def __init__(self) -> None:
        self.prompts = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return """
        {
            "summary": "ChatGPT has stronger product momentum.",
            "findings": ["ChatGPT shows more enterprise activity."],
            "risks": ["Evidence is based on a small article set."],
            "citations": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/openai-launch"
                }
            ]
        }
        """


def test_analyze_articles_builds_prompt_and_parses_llm_json() -> None:
    client = FakeLLMClient()

    result = analyze_articles(
        query_spec={
            "raw_query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment"],
        },
        articles=[
            {
                "company": "ChatGPT",
                "title": "Launch update",
                "source_name": "OpenAI",
                "content": "OpenAI launched a new enterprise feature.",
                "url": "https://example.com/openai-launch",
            }
        ],
        client=client,
    )

    assert result["summary"] == "ChatGPT has stronger product momentum."
    assert result["findings"] == ["ChatGPT shows more enterprise activity."]
    assert result["risks"] == ["Evidence is based on a small article set."]
    assert result["citations"][0]["url"] == "https://example.com/openai-launch"
    assert "Compare ChatGPT and Gemini" in client.prompts[0]
    assert "Launch update" in client.prompts[0]

class BadJSONClient:
    def complete(self, prompt: str) -> str:
        return "not json"


def test_analyze_articles_returns_fallback_when_llm_json_is_invalid() -> None:
    result = analyze_articles(
        query_spec={
            "raw_query": "Compare ChatGPT and Gemini sentiment in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment"],
        },
        articles=[],
        client=BadJSONClient(),
    )

    assert result["summary"] == "LLM analysis unavailable."
    assert result["findings"] == []
    assert result["risks"] == ["LLM returned invalid JSON."]
    assert result["citations"] == []

class PartialJSONClient:
    def complete(self, prompt: str) -> str:
        return '{"summary": "Partial analysis."}'

def test_analyze_articles_fills_missing_llm_json_fields() -> None:
    result = analyze_articles(
        query_spec={
            "raw_query": "Compare ChatGPT sentiment in the last 30 days",
            "companies": ["ChatGPT"],
            "time_range": "30d",
            "metrics": ["sentiment"],
        },
        articles=[],
        client=PartialJSONClient(),
    )

    assert result["summary"] == "Partial analysis."
    assert result["findings"] == []
    assert result["risks"] == []
    assert result["citations"] == []

class SchemaDriftJSONClient:
    def complete(self, prompt: str) -> str:
        return """
        {
            "summary": "Schema drift analysis.",
            "findings": "Single finding.",
            "risks": null,
            "citations": [
                {"title": "Missing URL"},
                "bad citation",
                {
                    "title": "Valid citation",
                    "url": "https://example.com/valid"
                }
            ]
        }
        """


def test_analyze_articles_normalizes_llm_json_field_types() -> None:
    result = analyze_articles(
        query_spec={
            "raw_query": "Compare ChatGPT sentiment in the last 30 days",
            "companies": ["ChatGPT"],
            "time_range": "30d",
            "metrics": ["sentiment"],
        },
        articles=[],
        client=SchemaDriftJSONClient(),
    )

    assert result["summary"] == "Schema drift analysis."
    assert result["findings"] == ["Single finding."]
    assert result["risks"] == []
    assert result["citations"] == [
        {
            "title": "Valid citation",
            "url": "https://example.com/valid",
        }
    ]

