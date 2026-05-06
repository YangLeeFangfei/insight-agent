from insight_agent.normalize.evidence import build_evidence_snippet


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
    llm_analysis: dict[str, object] | None = None,
) -> dict[str, object]:
    if llm_analysis is not None:
        findings = list(llm_analysis["findings"])
        findings.extend(llm_analysis.get("risks", []))

        articles_by_url = {
            article["url"]: article
            for article in articles or []
        }
        evidence = []
        ungrounded_citation_count = 0
        duplicate_citation_count = 0
        seen_citation_urls = set()
        for citation in llm_analysis.get("citations", []):
            citation_url = citation["url"]
            if citation_url in seen_citation_urls:
                duplicate_citation_count += 1
                continue

            seen_citation_urls.add(citation_url)
            article = articles_by_url.get(citation_url)
            if article is None:
                ungrounded_citation_count += 1
                continue

            snippet = build_evidence_snippet(
                article["content"],
                article["company"],
            )
            snippet["company"] = article["company"]
            snippet["title"] = article["title"]
            snippet["source_name"] = article["source_name"]
            snippet["url"] = article["url"]
            evidence.append(snippet)

        if ungrounded_citation_count:
            findings.append(f"Ungrounded citations dropped: {ungrounded_citation_count}")

        payload = build_report_payload(
            summary=llm_analysis["summary"],
            findings=findings,
            evidence=evidence,
        )
        payload["evidence_summary"] = {
            "grounded_citations": len(evidence),
            "ungrounded_citations": ungrounded_citation_count,
            "duplicate_citations": duplicate_citation_count,
        }
        payload["trace_events"] = run["events"]
        return payload

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

    sentiment_counts = {}

    for article in articles:
        sentiment = article["sentiment"]
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    sentiment_mix = ", ".join(
        f"{sentiment}={count}"
        for sentiment, count in sentiment_counts.items()
    )

    findings.append(f"Sentiment mix: {sentiment_mix}")

    evidence = []

    for article in articles:
        keyword = article["company"]
        snippet = build_evidence_snippet(article["content"], keyword)
        snippet["company"] = article["company"]
        snippet["title"] = article["title"]
        snippet["source_name"] = article["source_name"]
        snippet["url"] = article["url"]

        evidence.append(snippet)

    payload = build_report_payload(summary, findings, evidence)
    payload["trace_events"] = run["events"]
    return payload
