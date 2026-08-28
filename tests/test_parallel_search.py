import pytest

from app.config import get_settings
from app.parallel_search import parallel_live_search


def test_demo_search_is_explicitly_synthetic(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "true")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    get_settings.cache_clear()

    result = parallel_live_search(
        objective="Check access conditions for tomorrow's production plan.",
        search_queries=["road closures tomorrow", "rail disruption tomorrow"],
    )

    assert result["mode"] == "DEMO_NOT_LIVE"
    assert result["search_id"] == "demo-search"
    assert all(item["url"].startswith("demo://") for item in result["results"])

    get_settings.cache_clear()


def test_live_search_refuses_to_fake_missing_credentials(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "false")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="PARALLEL_API_KEY"):
        parallel_live_search(
            objective="Check a live dependency.",
            search_queries=["current production access"],
        )

    get_settings.cache_clear()
