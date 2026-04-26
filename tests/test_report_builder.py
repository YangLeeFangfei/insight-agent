from insight_agent.reporting.builder import build_report_payload


def test_build_report_payload_returns_structured_payload() -> None:
    payload = build_report_payload(
        summary="ChatGPT and Gemini both increased discussion volume.",
        findings=[
            "ChatGPT had stronger positive sentiment.",
            "Gemini showed more topic diversity.",
        ],
        evidence=[
            {
                "snippet_text": "OpenAI launched a new feature for enterprise teams.",
                "snippet_start": 0,
                "snippet_end": 42,
            }
        ],
    )

    assert payload["summary"] == "ChatGPT and Gemini both increased discussion volume."
    assert payload["findings"][0] == "ChatGPT had stronger positive sentiment."
    assert payload["evidence"][0]["snippet_text"].startswith("OpenAI launched")
