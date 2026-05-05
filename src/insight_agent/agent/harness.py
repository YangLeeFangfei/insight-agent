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
    
    status = "planned"

    if collection_request is not None:
        status = "collection_requested"

    return {
        "status": status,
        "plan": plan,
        "events": events,
    }

def record_collection_completed(
    run: dict[str, object],
    articles: list[dict[str, str]],
) -> dict[str, object]:
    companies = sorted({article["company"] for article in articles})

    run["events"].append(
        build_trace_event(
            "run.collection_completed",
            {
                "article_count": len(articles),
                "companies": companies,
            },
        )
    )
    run["status"] = "collection_completed"

    return run

def record_analysis_completed(
    run: dict[str, object],
    analysis: dict[str, object],
) -> dict[str, object]:
    findings = analysis.get("findings", [])
    citations = analysis.get("citations", [])

    run["events"].append(
        build_trace_event(
            "run.analysis_completed",
            {
                "summary": analysis.get("summary", ""),
                "finding_count": len(findings),
                "citation_count": len(citations),
            },
        )
    )
    run["status"] = "analysis_completed"

    return run

def record_report_completed(
    run: dict[str, object],
    report: dict[str, object],
) -> dict[str, object]:
    findings = report.get("findings", [])
    evidence = report.get("evidence", [])

    run["events"].append(
        build_trace_event(
            "run.report_completed",
            {
                "summary": report.get("summary", ""),
                "finding_count": len(findings),
                "evidence_count": len(evidence),
            },
        )
    )
    run["status"] = "report_completed"

    return run


def record_run_failed(
    run: dict[str, object],
    stage: str,
    error_message: str,
) -> dict[str, object]:
    run["events"].append(
        build_trace_event(
            "run.failed",
            {
                "stage": stage,
                "error_message": error_message,
            },
        )
    )
    run["status"] = "failed"

    return run
