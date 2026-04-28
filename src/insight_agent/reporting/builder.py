def build_report_payload(
    summary: str,
    findings: list[str],
    evidence: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "summary": summary,
        "findings": findings,
        "evidence": evidence,
    }

def build_preview_report(
    query_spec: dict[str, object],
    run: dict[str, object],
    articles: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    if not articles:
        companies = ", ".join(query_spec["companies"])
        metrics = ", ".join(query_spec["metrics"])
        source_types = ", ".join(query_spec["plan_preview"]["source_types"])
        stages = ", ".join(run["plan"]["stages"])

        summary = f"Prepared analysis run for {companies} across {query_spec['time_range']}."
        findings = [
            f"Metrics: {metrics}",
            f"Stages: {stages}",
        ]
        evidence = [
            {
                "snippet_text": f"Planned sources: {source_types}",
                "snippet_start": 0,
                "snippet_end": len(f"Planned sources: {source_types}"),
            }
        ]

        return build_report_payload(summary, findings, evidence)
    
    companies = ", ".join(sorted({article["company"] for article in articles}))
    article_count = len(articles)

    summary = (
        f"Prepared analysis run for {companies} across "
        f"{query_spec['time_range']} with {article_count} articles."
    )
    findings = [
        f"Companies covered: {companies}",
        f"Article count: {article_count}",
    ]

    first_article = articles[0]
    evidence_text = first_article["content"]
    evidence = [
        {
            "snippet_text": evidence_text,
            "snippet_start": 0,
            "snippet_end": len(evidence_text),
        }
    ]

    return build_report_payload(summary, findings, evidence)



