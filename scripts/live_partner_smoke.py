"""Minimal qualifying smoke test for the Parallel runtime integration.

Run only with a real PARALLEL_API_KEY and SETWATCH_DEMO_MODE=false.
"""

import json

from app.config import get_settings
from app.parallel_search import parallel_live_search


def main() -> None:
    settings = get_settings()
    if settings.demo_mode:
        raise SystemExit("Refusing: SETWATCH_DEMO_MODE must be false for a live partner smoke test")
    if not settings.parallel_api_key:
        raise SystemExit("Refusing: PARALLEL_API_KEY is not configured")

    result = parallel_live_search(
        objective=(
            "Find current public information that could materially affect vehicle and crew access "
            "to a central London film production tomorrow morning, focusing on major closures, "
            "transport disruption, and exceptional public events."
        ),
        search_queries=[
            "central London road closures tomorrow",
            "London transport disruption tomorrow",
            "central London major events tomorrow",
        ],
    )
    print(json.dumps(result, indent=2, default=str))

    if result.get("mode") != "LIVE_PARALLEL_SEARCH":
        raise SystemExit("FAIL: result was not marked as live Parallel Search")
    if not result.get("search_id"):
        raise SystemExit("FAIL: Parallel response did not expose a search_id")
    if not result.get("results"):
        raise SystemExit("FAIL: Parallel response contained no search results")

    print("\nPASS: live Parallel Search returned a search_id and evidence records")


if __name__ == "__main__":
    main()
