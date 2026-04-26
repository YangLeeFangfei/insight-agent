from insight_agent.agent.harness import build_run_plan, initialize_run

def test_build_run_plan_returns_execution_stages() -> None:
    plan = build_run_plan(
        {
            "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment", "topics"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        }
    )  
    assert plan["query"] == "Compare ChatGPT and Gemini in the last 30 days"
    assert plan["needs_confirmation"] is True
    assert plan["stages"] == [
        "plan_preview",
        "source_collection",
        "normalization",
        "analysis",
        "evidence_binding",
        "reporting",
    ]

def test_initialize_run_returns_plan_and_trace_events() -> None:
    run = initialize_run(
        {
            "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
            "companies": ["ChatGPT", "Gemini"],
            "time_range": "30d",
            "metrics": ["sentiment", "topics"],
            "plan_preview": {
                "needs_confirmation": True,
                "source_types": ["news", "announcement", "industry"],
            },
        }
    )

    assert run["plan"]["query"] == "Compare ChatGPT and Gemini in the last 30 days"
    assert run["events"][0]["event_type"] == "run.started"
    assert run["events"][1]["event_type"] == "run.plan_generated"
