from insight_agent.reporting.evidence_quality import normalize_evidence_summary


def test_normalize_evidence_summary_returns_counts() -> None:
    summary = normalize_evidence_summary(
        {
            "grounded_citations": 2,
            "ungrounded_citations": 1,
            "duplicate_citations": 3,
        }
    )

    assert summary == {
        "grounded_citations": 2,
        "ungrounded_citations": 1,
        "duplicate_citations": 3,
    }


def test_normalize_evidence_summary_defaults_missing_counts() -> None:
    summary = normalize_evidence_summary(
        {
            "grounded_citations": 2,
        }
    )

    assert summary == {
        "grounded_citations": 2,
        "ungrounded_citations": 0,
        "duplicate_citations": 0,
    }


def test_normalize_evidence_summary_rejects_invalid_counts() -> None:
    summary = normalize_evidence_summary(
        {
            "grounded_citations": "<script>alert('grounded')</script>",
            "ungrounded_citations": -1,
            "duplicate_citations": True,
        }
    )

    assert summary == {
        "grounded_citations": 0,
        "ungrounded_citations": 0,
        "duplicate_citations": 0,
    }


def test_normalize_evidence_summary_defaults_non_dict_input() -> None:
    summary = normalize_evidence_summary(None)

    assert summary == {
        "grounded_citations": 0,
        "ungrounded_citations": 0,
        "duplicate_citations": 0,
    }
