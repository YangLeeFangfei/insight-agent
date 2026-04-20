import re


def parse_query(raw_query: str):
    metrics = []
    lowered = raw_query.lower()
    companies_result = []
    time_range = "7d"
    if "chatgpt" in lowered:
        companies_result.append("ChatGPT")
    if "gemini" in lowered:
        companies_result.append("Gemini")
    if "sentiment" in lowered:
        metrics.append("sentiment")
    if "topic" in lowered:
        metrics.append("topics")
    match = re.search(r"(\d+)\s*d", lowered)
    if match:
        time_range = f"{match.group(1)}d" # 返回匹配的第一个括号内容
    return {
        "raw_query": raw_query,
        "companies": companies_result,
        "time_range": time_range,
        "metrics": metrics,
        "plan_preview": {
        "needs_confirmation": True,
        "source_types": ["news", "announcement", "industry"],
        },
    }
