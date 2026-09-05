import pytest

from app.config import get_settings
from app.runtime import (
    _extract_json,
    _mandatory_search_request,
    _validated_result,
    run_setwatch,
)


def _trace(url: str = "https://example.com/notice") -> list[dict]:
    return [
        {
            "mode": "LIVE_PARALLEL_SEARCH",
            "search_id": "search-123",
            "objective": "Check access",
            "search_queries": ["road closure"],
            "result_count": 1,
            "sources": [{"title": "Notice", "url": url, "publish_date": None}],
        }
    ]


def _payload(source_url: str, overall: str = "GO", finding: str = "GO") -> str:
    return f'''{{
      "overall_status": "{overall}",
      "summary": "Current evidence requires a bounded decision.",
      "assumptions_checked": 99,
      "findings": [{{
        "status": "{finding}",
        "assumption": "Access remains open",
        "evidence": "A current notice was reviewed.",
        "inference": "Access may be affected.",
        "consequence": "The unit could be delayed.",
        "recommended_action": "Confirm before dispatch.",
        "confidence": "medium",
        "sources": [{{"title": "Notice", "url": "{source_url}", "publish_date": null}}]
      }}],
      "change_note": null
    }}'''


def test_extract_json_accepts_plain_and_fenced_objects():
    assert _extract_json('{"overall_status":"GO"}')["overall_status"] == "GO"
    assert _extract_json('```json\n{"overall_status":"VERIFY"}\n```')["overall_status"] == "VERIFY"


def test_validation_enforces_worst_status_and_actual_count():
    result, valid, integrity = _validated_result(
        _payload("https://example.com/notice", overall="GO", finding="CHANGE"), _trace()
    )
    assert valid is True
    assert integrity == "verified"
    assert result.overall_status == "CHANGE"
    assert result.assumptions_checked == 1


def test_validation_rejects_model_invented_source():
    result, valid, integrity = _validated_result(
        _payload("https://invented.example/claim"), _trace()
    )
    assert valid is True
    assert integrity == "degraded"
    assert result.overall_status == "VERIFY"
    assert result.findings[0].sources == []
    assert result.findings[0].confidence == "low"


def test_invalid_output_fails_conservatively():
    result, valid, integrity = _validated_result("not json", _trace())
    assert valid is False
    assert integrity == "degraded"
    assert result.overall_status == "VERIFY"
    assert result.raw_response == "not json"


def test_mandatory_search_request_uses_location_and_date():
    objective, queries = _mandatory_search_request(
        "fallback prompt",
        production_plan="A dawn exterior with vehicle access.",
        production_date="2026-09-06",
        location_context="Stonehenge visitor area, Wiltshire, UK",
    )
    assert "Stonehenge visitor area, Wiltshire, UK" in objective
    assert "2026-09-06" in objective
    assert len(queries) == 4
    assert all("Stonehenge visitor area" in query for query in queries)


@pytest.mark.asyncio
async def test_live_run_calls_parallel_before_gemini(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "false")
    monkeypatch.setenv("PARALLEL_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    get_settings.cache_clear()
    calls: list[str] = []

    def fake_search(objective: str, search_queries: list[str]):
        from app.trace import record_partner_search

        calls.append("parallel")
        response = {
            "mode": "LIVE_PARALLEL_SEARCH",
            "objective": objective,
            "search_queries": search_queries,
            "search_id": "search-required",
            "results": [
                {
                    "title": "Current notice",
                    "url": "https://example.com/notice",
                    "publish_date": None,
                    "excerpts": ["Access requires confirmation."],
                }
            ],
        }
        record_partner_search(response)
        return response

    async def fake_agent_text(agent, prompt: str, app_name: str = "setwatch"):
        calls.append("gemini")
        assert "MANDATORY PARALLEL EVIDENCE" in prompt
        assert "search-required" in prompt
        return _payload("https://example.com/notice", finding="VERIFY")

    monkeypatch.setattr("app.runtime.parallel_live_search", fake_search)
    monkeypatch.setattr("app.runtime._run_agent_text", fake_agent_text)
    outcome = await run_setwatch(
        "A sufficiently detailed live production plan.",
        production_plan="Exterior filming with vehicle access before first light.",
        production_date="2026-09-06",
        location_context="Stonehenge, Wiltshire, UK",
    )
    assert calls == ["parallel", "gemini"]
    assert outcome.meta.mode == "live"
    assert outcome.meta.partner_search_count == 1
    assert outcome.meta.partner_traces[0].search_id == "search-required"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_demo_run_needs_no_google_credentials(monkeypatch):
    monkeypatch.setenv("SETWATCH_DEMO_MODE", "true")
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    get_settings.cache_clear()
    outcome = await run_setwatch("A sufficiently detailed synthetic production plan.")
    assert outcome.meta.mode == "demo"
    assert outcome.meta.partner_traces[0].mode == "DEMO_NOT_LIVE"
    assert outcome.result.overall_status == "VERIFY"
    get_settings.cache_clear()
