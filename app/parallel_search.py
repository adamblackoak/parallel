from __future__ import annotations

from typing import Any

from parallel import Parallel

from app.config import get_settings


def _demo_results(objective: str, search_queries: list[str]) -> dict[str, Any]:
    """Clearly-labelled synthetic results for local UI development only."""
    return {
        "mode": "DEMO_NOT_LIVE",
        "objective": objective,
        "search_queries": search_queries,
        "search_id": "demo-search",
        "results": [
            {
                "title": "Synthetic transport notice",
                "url": "demo://transport-notice",
                "publish_date": None,
                "excerpts": [
                    "Synthetic development fixture: a planned road closure may affect access between 06:00 and 11:00."
                ],
            },
            {
                "title": "Synthetic location notice",
                "url": "demo://location-notice",
                "publish_date": None,
                "excerpts": [
                    "Synthetic development fixture: pedestrian access remains open but vehicle loading requires confirmation."
                ],
            },
        ],
    }


def parallel_live_search(objective: str, search_queries: list[str]) -> dict[str, Any]:
    """Search the live web with Parallel for time-sensitive production evidence.

    Use this tool whenever the production plan contains an external assumption that
    may have changed. Supply one precise natural-language objective and 2-4 short,
    diverse search queries. Do not use it for facts already contained in the plan.
    """
    settings = get_settings()

    cleaned_queries = [q.strip() for q in search_queries if q and q.strip()][:4]
    if not cleaned_queries:
        raise ValueError("At least one non-empty search query is required")

    if settings.demo_mode:
        return _demo_results(objective, cleaned_queries)

    if not settings.parallel_api_key:
        raise RuntimeError("PARALLEL_API_KEY is required for a live SetWatch run")

    client = Parallel(api_key=settings.parallel_api_key)
    search = client.search(
        objective=objective.strip(),
        search_queries=cleaned_queries,
        mode=settings.search_mode,
    )

    results: list[dict[str, Any]] = []
    for item in list(search.results)[: settings.max_search_results]:
        results.append(
            {
                "title": getattr(item, "title", None),
                "url": getattr(item, "url", None),
                "publish_date": getattr(item, "publish_date", None),
                "excerpts": list(getattr(item, "excerpts", []) or []),
            }
        )

    return {
        "mode": "LIVE_PARALLEL_SEARCH",
        "objective": objective,
        "search_queries": cleaned_queries,
        "search_id": getattr(search, "search_id", None),
        "results": results,
    }
