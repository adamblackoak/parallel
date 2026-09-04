"""End-to-end qualifying smoke test for Google ADK, Gemini and Parallel."""

from __future__ import annotations

import asyncio
import json

from app.config import get_settings
from app.runtime import run_setwatch

PLAN = """
Unit call 05:30 for an exterior sequence in central London from 07:00 to 10:30.
Two 7.5-tonne trucks require loading access from 05:45. Crew transfer depends on
the nearest rail station operating normally. Rain cover is limited and the
exterior sequence cannot tolerate heavy rain. Check current closures, major
events, access restrictions, severe weather and transport disruption that could
materially affect the plan.
""".strip()


async def main() -> None:
    settings = get_settings()
    if settings.demo_mode:
        raise SystemExit("Refusing: SETWATCH_DEMO_MODE must be false")
    if not settings.live_ready:
        raise SystemExit(
            "Refusing: GOOGLE_CLOUD_PROJECT and PARALLEL_API_KEY must be configured"
        )

    outcome = await run_setwatch(
        "Run a SetWatch pre-flight check. Use live Parallel Search before reaching "
        f"a conclusion.\n\nPRODUCTION PLAN\n{PLAN}"
    )
    payload = {
        "result": outcome.result.model_dump(mode="json"),
        "meta": outcome.meta.model_dump(mode="json"),
    }
    print(json.dumps(payload, indent=2))

    if outcome.meta.mode != "live":
        raise SystemExit("FAIL: runtime was not live")
    if not outcome.meta.output_validated:
        raise SystemExit("FAIL: model output did not satisfy the response schema")
    live_traces = [
        trace
        for trace in outcome.meta.partner_traces
        if trace.mode == "LIVE_PARALLEL_SEARCH"
    ]
    if not live_traces:
        raise SystemExit("FAIL: no live Parallel trace was captured")
    if not all(trace.search_id for trace in live_traces):
        raise SystemExit("FAIL: a Parallel trace did not expose a search ID")
    if not outcome.result.findings:
        raise SystemExit("FAIL: no validated findings were returned")

    print("\nPASS: Google ADK/Gemini completed with captured live Parallel evidence")


if __name__ == "__main__":
    asyncio.run(main())
