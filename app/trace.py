from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any

_partner_traces: ContextVar[tuple[dict[str, Any], ...]] = ContextVar(
    "setwatch_partner_traces", default=()
)


def start_trace() -> Token[tuple[dict[str, Any], ...]]:
    return _partner_traces.set(())


def record_partner_search(search: dict[str, Any]) -> None:
    results = search.get("results") or []
    sources = [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "publish_date": (
                str(item["publish_date"]) if item.get("publish_date") is not None else None
            ),
        }
        for item in results
        if item.get("url")
    ]
    event = {
        "mode": search["mode"],
        "search_id": search.get("search_id"),
        "objective": search.get("objective") or "",
        "search_queries": list(search.get("search_queries") or []),
        "result_count": len(results),
        "sources": sources,
    }
    _partner_traces.set((*_partner_traces.get(), event))


def current_traces() -> list[dict[str, Any]]:
    return [dict(event) for event in _partner_traces.get()]


def close_trace(token: Token[tuple[dict[str, Any], ...]]) -> None:
    _partner_traces.reset(token)
