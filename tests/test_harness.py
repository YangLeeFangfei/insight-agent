from insight_agent.agent.harness import (
    build_run_plan,
    initialize_run,
    record_collection_completed,
    record_analysis_completed,
    record_report_completed,
    record_run_failed,
)
from insight_agent.collectors.base import CollectionRequest


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

def test_initialize_run_records_collection_request() -> None:
    query_spec = {
        "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
        "companies": ["ChatGPT", "Gemini"],
        "time_range": "30d",
        "metrics": ["sentiment", "topics"],
        "plan_preview": {
            "needs_confirmation": True,
            "source_types": ["news", "announcement", "industry"],
        },
    }
    collection_request = CollectionRequest(
        companies=["ChatGPT", "Gemini"],
        time_range="30d",
        source_types=["news", "announcement", "industry"],
    )

    run = initialize_run(query_spec, collection_request)

    assert run["events"][2]["event_type"] == "run.collection_requested"
    assert run["events"][2]["payload"]["companies"] == ["ChatGPT", "Gemini"]
    assert run["events"][2]["payload"]["time_range"] == "30d"
    assert run["events"][2]["payload"]["source_types"] == [
        "news",
        "announcement",
        "industry",
    ]

def test_record_collection_completed_adds_trace_event() -> None:
    query_spec = {
        "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
        "companies": ["ChatGPT", "Gemini"],
        "time_range": "30d",
        "metrics": ["sentiment", "topics"],
        "plan_preview": {
            "needs_confirmation": True,
            "source_types": ["news", "announcement", "industry"],
        },
    }
    collection_request = CollectionRequest(
        companies=["ChatGPT", "Gemini"],
        time_range="30d",
        source_types=["news", "announcement", "industry"],
    )
    run = initialize_run(query_spec, collection_request)

    updated_run = record_collection_completed(
        run,
        [
            {"company": "ChatGPT"},
            {"company": "Gemini"},
        ],
    )

    event = updated_run["events"][-1]

    assert event["event_type"] == "run.collection_completed"
    assert event["payload"]["article_count"] == 2
    assert event["payload"]["companies"] == ["ChatGPT", "Gemini"]
    assert updated_run["status"] == "collection_completed"

def test_initialize_run_sets_current_status() -> None:
    query_spec = {
        "raw_query": "Compare ChatGPT and Gemini in the last 30 days",
        "companies": ["ChatGPT", "Gemini"],
        "time_range": "30d",
        "metrics": ["sentiment", "topics"],
        "plan_preview": {
            "needs_confirmation": True,
            "source_types": ["news", "announcement", "industry"],
        },
    }
    collection_request = CollectionRequest(
        companies=["ChatGPT", "Gemini"],
        time_range="30d",
        source_types=["news", "announcement", "industry"],
    )

    run = initialize_run(query_spec, collection_request)

    assert run["status"] == "collection_requested"

def test_record_analysis_completed_adds_trace_event_and_status() -> None:
    run = {
        "status": "collection_completed",
        "plan": {
            "stages": [
                "plan_preview",
                "source_collection",
                "normalization",
                "analysis",
                "evidence_binding",
                "reporting",
            ]
        },
        "events": [],
    }

    updated_run = record_analysis_completed(
        run,
        {
            "summary": "LLM summary.",
            "findings": ["Finding one."],
            "risks": [],
            "citations": [
                {
                    "title": "Launch update",
                    "url": "https://example.com/launch",
                }
            ],
        },
    )

    event = updated_run["events"][-1]

    assert event["event_type"] == "run.analysis_completed"
    assert event["payload"]["summary"] == "LLM summary."
    assert event["payload"]["finding_count"] == 1
    assert event["payload"]["citation_count"] == 1
    assert updated_run["status"] == "analysis_completed"

def test_record_report_completed_adds_trace_event_and_status() -> None:
    run = {
        "status": "analysis_completed",
        "plan": {
            "stages": [
                "plan_preview",
                "source_collection",
                "normalization",
                "analysis",
                "evidence_binding",
                "reporting",
            ]
        },
        "events": [],
    }

    updated_run = record_report_completed(
        run,
        {
            "summary": "Report summary.",
            "findings": ["Finding one.", "Finding two."],
            "evidence": [
                {"title": "Evidence one"},
            ],
        },
    )

    event = updated_run["events"][-1]

    assert event["event_type"] == "run.report_completed"
    assert event["payload"]["summary"] == "Report summary."
    assert event["payload"]["finding_count"] == 2
    assert event["payload"]["evidence_count"] == 1
    assert updated_run["status"] == "report_completed"


def test_record_run_failed_adds_trace_event_and_status() -> None:
    run = {
        "status": "analysis_completed",
        "plan": {
            "stages": [
                "plan_preview",
                "source_collection",
                "normalization",
                "analysis",
                "evidence_binding",
                "reporting",
            ]
        },
        "events": [],
    }

    updated_run = record_run_failed(
        run,
        stage="reporting",
        error_message="HTML report failed.",
    )

    event = updated_run["events"][-1]

    assert event["event_type"] == "run.failed"
    assert event["payload"]["stage"] == "reporting"
    assert event["payload"]["error_message"] == "HTML report failed."
    assert updated_run["status"] == "failed"
