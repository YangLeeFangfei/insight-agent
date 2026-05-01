from insight_agent.collectors.base import build_collection_request

def test_build_collection_request_from_query_spec() -> None:
    query_spec = {
        "companies": ["ChatGPT", "Gemini"],
        "time_range": "30d",
        "plan_preview": {
            "source_types": ["news", "announcement", "industry"],
        },
    }

    request = build_collection_request(query_spec)

    
    assert request.companies == ["ChatGPT", "Gemini"]
    assert request.time_range == "30d"
    assert request.source_types == ["news", "announcement", "industry"]