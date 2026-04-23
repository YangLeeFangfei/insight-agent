def validate_read_only_sql(query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized.startswith("select"):
        return False
    
    forbidden = [" insert ", " update ", " delete ", " drop ", " alter ", ";"]
    return not any(token in normalized for token in forbidden)