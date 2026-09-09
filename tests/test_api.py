from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import _requested_previous_snapshot, app
from app.models import CheckRequest


def test_health_exposes_configuration_without_secrets(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "false")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    get_settings.cache_clear()
    payload = TestClient(app).get("/health").json()
    assert payload["live_ready"] is False
    assert set(payload["missing_live_configuration"]) == {
        "PARALLEL_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
    }
    assert "api_key" not in payload
    get_settings.cache_clear()


def test_demo_api_runs_without_external_credentials(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "true")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    get_settings.cache_clear()
    response = TestClient(app).post(
        "/api/check",
        json={"plan": "Exterior filming with truck access required before first light."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["mode"] == "demo"
    assert payload["meta"]["partner_search_count"] == 1
    assert payload["result"]["overall_status"] == "VERIFY"
    get_settings.cache_clear()


def test_live_api_refuses_unconfigured_run(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "false")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    get_settings.cache_clear()
    response = TestClient(app).post(
        "/api/check",
        json={"plan": "Exterior filming with truck access required before first light."},
    )
    assert response.status_code == 503
    assert "PARALLEL_API_KEY" in response.json()["detail"]
    get_settings.cache_clear()


def test_previous_snapshot_is_ignored_without_explicit_comparison():
    stale = {"summary": "Stonehenge stale result"}
    request = CheckRequest(
        plan="Exterior filming with truck access required before first light.",
        previous_snapshot=stale,
    )
    assert _requested_previous_snapshot(request) is None


def test_previous_snapshot_is_used_only_with_explicit_comparison():
    stale = {"summary": "Stonehenge stale result"}
    request = CheckRequest(
        plan="Exterior filming with truck access required before first light.",
        compare_with_previous=True,
        previous_snapshot=stale,
    )
    assert _requested_previous_snapshot(request) == stale


def test_browser_comparison_is_opt_in_and_legacy_snapshot_is_retired():
    body = TestClient(app).get("/").text
    assert 'id="compare" type="checkbox" disabled' in body
    assert "compare_with_previous:compare" in body
    assert "localStorage.removeItem(legacyPreviousKey)" in body
