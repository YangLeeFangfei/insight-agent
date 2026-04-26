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
