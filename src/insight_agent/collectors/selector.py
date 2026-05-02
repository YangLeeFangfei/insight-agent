from insight_agent.collectors.base import CollectionRequest
from insight_agent.collectors.demo import collect_demo_articles
from insight_agent.collectors.news import collect_news_articles
from insight_agent.config import get_collector_mode


def collect_articles(request: CollectionRequest) -> list[dict[str, str]]:
    mode = get_collector_mode()

    if mode == "news":
        return collect_news_articles(request)

    return collect_demo_articles(request)
