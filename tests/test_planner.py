from insight_agent.agent.planner import parse_query

def test_parse_query_extracts_companies_and_time_range():
    result = parse_query("Compare ChatGPT and Gemini in the last 30 days")

    assert result["raw_query"] == "Compare ChatGPT and Gemini in the last 30 days"
    assert result["companies"] == ["ChatGPT", "Gemini"]
    assert result["time_range"] == "30d"


def test_parse_query_builds_plan_preview_metrics():
    result = parse_query("Compare ChatGPT and Gemini sentiment and topics in the last 30 days")

    assert result["metrics"] == ["sentiment", "topics"]
    assert result["plan_preview"]["needs_confirmation"] is True
    assert result["plan_preview"]["source_types"] == ["news", "announcement", "industry"]