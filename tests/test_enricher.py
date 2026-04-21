from insight_agent.normalize.cleaner import normalize_article
from insight_agent.normalize.evidence import build_evidence_snippet

def test_normalize_article_strips_title_and_source_type() -> None:
    article = normalize_article(
        {
            "company": "ChatGPT",
            "title": "  Launch Update  ",
            "source_name": "OpenAI Blog",
            "source_type": "Announcement",
            "content": "OpenAI launched a new feature for enterprise teams.",
            "published_date": "2026-04-20",
            "collected_at": "2026-04-20T10:00:00",
            "url": "https://example.com/a",
            "sentiment": "positive",
        }
    )

    assert article["title"] == "Launch Update"
    assert article["source_type"] == "announcement"


def test_build_evidence_snippet_returns_bounded_snippet() -> None:
    snippet = build_evidence_snippet(
        "OpenAI launched a new feature for enterprise teams on Tuesday.",
        keyword="enterprise",
    )

    assert "enterprise" in snippet["snippet_text"].lower()
    assert snippet["snippet_start"] >= 0
    assert snippet["snippet_end"] > snippet["snippet_start"]