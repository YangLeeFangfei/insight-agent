from insight_agent.agent.trace import build_trace_event


def test_build_trace_event_returns_structured_event() -> None:
    event = build_trace_event(
        "run.started",
        {"query": "Compare ChatGPT and Gemini"},
    )

    assert event["event_type"] == "run.started"
    assert event["payload"]["query"] == "Compare ChatGPT and Gemini"


