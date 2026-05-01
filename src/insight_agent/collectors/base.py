from dataclasses import dataclass

@dataclass(frozen=True)
class CollectionRequest:
    companies: list[str]
    time_range: str
    source_types: list[str]


def build_collection_request(query_spec: dict[str, object]) -> CollectionRequest:
    plan_preview = query_spec["plan_preview"]

    return CollectionRequest(
        companies=query_spec["companies"],
        time_range=query_spec["time_range"],
        source_types=plan_preview["source_types"],
    )