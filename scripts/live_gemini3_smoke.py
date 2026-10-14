"""Opt-in, billed Google Cloud probe; no deployment or cache-policy mutations.

Use synthetic inputs only, after the test project's cache policy is reviewed.
"""
import asyncio

from google.adk import Agent

from app.agent import citation_repair_agent, generation_config
from app.config import get_settings
from app.runtime import _run_agent_text, _validated_result


async def main() -> None:
    settings = get_settings()
    if settings.demo_mode or not settings.google_cloud_project:
        raise SystemExit("Requires a configured live Google Cloud test project")
    if settings.gemini_model != "gemini-3.5-flash-lite":
        raise SystemExit("Set GEMINI_MODEL=gemini-3.5-flash-lite in the test process")
    calls = []

    def synthetic_lookup(subject: str) -> dict:
        """Retrieve synthetic access evidence, then transport evidence."""
        calls.append(subject)
        return {"subject": subject, "next_subject": "transport" if subject == "access" else None}

    probe = Agent(
        name="gemini3_compatibility_probe",
        model=settings.gemini_model,
        tools=[synthetic_lookup],
        instruction=(
            "Call synthetic_lookup for access. After receiving its result, call it "
            "for the next_subject it returns. Then return the single word COMPLETE."
        ),
        generate_content_config=generation_config(settings.gemini_model),
    )
    text = await _run_agent_text(probe, "Execute the synthetic two-step lookup")
    if calls != ["access", "transport"] or text.strip() != "COMPLETE":
        raise SystemExit(f"FAIL: tool loop did not complete as required: {calls!r}")

    url = "https://example.com/synthetic-notice"
    trace = [{"sources": [{"title": "Synthetic notice", "url": url, "publish_date": None}]}]
    prompt = (
        'Return a SetWatch JSON result with one VERIFY finding: access requires confirmation. '
        'This is synthetic evidence only. ALLOWED LIVE SOURCES: '
        f'{url}: access is not confirmed. Cite this exact URL.'
    )
    repaired = await _run_agent_text(citation_repair_agent, prompt, app_name="gemini3-repair-probe")
    result, valid, integrity = _validated_result(repaired, trace)
    if not valid or integrity != "verified" or result.overall_status != "VERIFY":
        raise SystemExit("FAIL: repair-agent JSON/source binding")
    print("PASS: live Gemini sequential tool loop and repair-agent JSON; synthetic inputs only")


if __name__ == "__main__":
    asyncio.run(main())
