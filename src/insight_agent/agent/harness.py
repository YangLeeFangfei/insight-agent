from insight_agent.agent.trace import build_trace_event
from insight_agent.collectors.base import CollectionRequest

def build_run_plan(query_spec: dict[str, object]) -> dict[str, object]:
    plan_preview = query_spec.get("plan_preview", {})

    return {
        "query": query_spec["raw_query"],
        "needs_confirmation": plan_preview.get("needs_confirmation", True),
        "stages": [
            "plan_preview",
            "source_collection",
            "normalization",
            "analysis",
            "evidence_binding",
            "reporting",
        ],
    }

def initialize_run(query_spec: dict[str, object], collection_request: CollectionRequest | None = None,) -> dict[str, object]:

    plan = build_run_plan(query_spec)

    events = [
        build_trace_event(
            "run.started",
            {"query": query_spec["raw_query"]},
        ),
        build_trace_event(
            "run.plan_generated",
            {"stages": plan["stages"]},
        ),
    ]

    if collection_request is not None:
        events.append(
            build_trace_event(
                "run.collection_requested",
                {
                    "companies": collection_request.companies,
                    "time_range": collection_request.time_range,
                    "source_types": collection_request.source_types,
                },
            )
        )

    return {
        "plan": plan,
        "events": events,
    }
