
def build_evidence_snippet(content: str, keyword:str) -> dict[str, object]:
    lowered = content.lower()
    keyword_lower = keyword.lower()
    start = lowered.find(keyword_lower)
    if start == -1:
        start = 0
    
    end = min(start + 80, len(content))

    return {
        "snippet_text": content[start:end],
        "snippet_start": start,
        "snippet_end" : end,
    }