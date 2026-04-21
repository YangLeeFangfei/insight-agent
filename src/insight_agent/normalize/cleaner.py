
def normalize_article(article: dict[str, str]) -> dict[str, str]:
    normalized = dict(article)
    normalized["title"] = article["title"].strip()
    normalized["source_type"] = article["source_type"].strip().lower()
    normalized["content"] = article["content"].strip()
    return normalized

