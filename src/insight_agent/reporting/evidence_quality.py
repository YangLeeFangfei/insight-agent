EVIDENCE_SUMMARY_DEFAULTS = {
    "grounded_citations": 0,
    "ungrounded_citations": 0,
    "duplicate_citations": 0,
}


def _normalize_count(value: object) -> int:
    if isinstance(value, bool):
        return 0

    if isinstance(value, int) and value >= 0:
        return value

    return 0


def normalize_evidence_summary(summary: object) -> dict[str, int]:
    if not isinstance(summary, dict):
        return dict(EVIDENCE_SUMMARY_DEFAULTS)

    return {
        key: _normalize_count(summary.get(key, default))
        for key, default in EVIDENCE_SUMMARY_DEFAULTS.items()
    }
