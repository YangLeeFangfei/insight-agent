import json
from typing import Protocol

class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        ...

def build_analysis_prompt(
    query_spec: dict[str, object],
    articles: list[dict[str, str]],
) -> str:
    article_lines = []

    for article in articles:
        article_lines.append(
            "\n".join(
                [
                    f"Company: {article['company']}",
                    f"Title: {article['title']}",
                    f"Source: {article['source_name']}",
                    f"Content: {article['content']}",
                    f"URL: {article['url']}",
                ]
            )
        )
    
    articles_text = "\n".join(article_lines)
    return f"""
You are an analyst for competitive intelligence.

User query:
{query_spec["raw_query"]}

Return JSON with:
summary: string
findings: list of strings
risks: list of strings
citations: list of objects with title and url

Articles:
{articles_text}
"""

def _normalize_string_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]

    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, str)]


def _normalize_citations(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []

    citations = []

    for item in value:
        if not isinstance(item, dict):
            continue

        title = item.get("title")
        url = item.get("url")

        if not isinstance(title, str) or not isinstance(url, str):
            continue

        citations.append(
            {
                "title": title,
                "url": url,
            }
        )

    return citations


def _normalize_llm_analysis(parsed: object) -> dict[str, object]:
    if not isinstance(parsed, dict):
        return {
            "summary": "LLM analysis unavailable.",
            "findings": [],
            "risks": ["LLM returned non-object JSON."],
            "citations": [],
        }

    summary = parsed.get("summary", "LLM analysis unavailable.")
    if not isinstance(summary, str):
        summary = "LLM analysis unavailable."

    return {
        "summary": summary,
        "findings": _normalize_string_list(parsed.get("findings", [])),
        "risks": _normalize_string_list(parsed.get("risks", [])),
        "citations": _normalize_citations(parsed.get("citations", [])),
    }

def analyze_articles(
    query_spec: dict[str, object],
    articles: list[dict[str, str]],
    client: LLMClient,
) -> dict[str, object]:
    prompt = build_analysis_prompt(query_spec, articles)
    response_text = client.complete(prompt)

    try:
        parsed = json.loads(response_text)

        return _normalize_llm_analysis(parsed)

    except json.JSONDecodeError:
        return {
            "summary": "LLM analysis unavailable.",
            "findings": [],
            "risks": ["LLM returned invalid JSON."],
            "citations": [],
        }
