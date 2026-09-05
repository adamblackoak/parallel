from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import ValidationError

from app.agent import root_agent
from app.config import get_settings
from app.models import PartnerTrace, RunMeta, SetWatchResult
from app.parallel_search import parallel_live_search
from app.trace import close_trace, current_traces, start_trace

APP_NAME = "setwatch"
STATUS_RANK = {"GO": 0, "VERIFY": 1, "CHANGE": 2}


@dataclass(frozen=True)
class RunOutcome:
    result: SetWatchResult
    meta: RunMeta


def _extract_json(text: str) -> dict[str, Any] | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        if candidate.startswith("json"):
            candidate = candidate[4:].lstrip()
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(candidate[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass
    return None


def _conservative_result(raw_response: str) -> SetWatchResult:
    return SetWatchResult(
        overall_status="VERIFY",
        summary="The agent response could not be validated and requires human review.",
        assumptions_checked=0,
        findings=[],
        change_note=None,
        raw_response=raw_response,
    )


def _validated_result(
    raw_response: str, traces: list[dict[str, Any]]
) -> tuple[SetWatchResult, bool, str]:
    payload = _extract_json(raw_response)
    if payload is None:
        return _conservative_result(raw_response), False, "degraded"
    try:
        result = SetWatchResult.model_validate(payload)
    except ValidationError:
        return _conservative_result(raw_response), False, "degraded"

    allowed_urls = {
        source["url"]
        for trace in traces
        for source in trace.get("sources", [])
        if source.get("url")
    }
    integrity_degraded = False
    for finding in result.findings:
        cited = finding.sources
        finding.sources = [source for source in cited if source.url in allowed_urls]
        if len(finding.sources) != len(cited):
            integrity_degraded = True
        if not finding.sources:
            finding.status = "VERIFY"
            finding.confidence = "low"
            integrity_degraded = True

    result.assumptions_checked = len(result.findings)
    if result.findings:
        result.overall_status = max(
            (finding.status for finding in result.findings), key=STATUS_RANK.__getitem__
        )
    else:
        result.overall_status = "VERIFY"
        integrity_degraded = True

    return result, True, "degraded" if integrity_degraded else "verified"


def _demo_result() -> SetWatchResult:
    evidence = parallel_live_search(
        objective="Demonstrate a SetWatch production access pre-flight without live services.",
        search_queries=["synthetic road closure", "synthetic location access"],
    )
    sources = [
        {
            "title": item.get("title"),
            "url": item["url"],
            "publish_date": item.get("publish_date"),
        }
        for item in evidence["results"]
    ]
    return SetWatchResult(
        overall_status="VERIFY",
        summary="Demo fixture: vehicle loading access requires confirmation before unit movement.",
        assumptions_checked=1,
        findings=[
            {
                "status": "VERIFY",
                "assumption": "Vehicle and pedestrian access remain compatible with the call plan.",
                "evidence": "Synthetic notices indicate a possible road closure and a separate loading-access condition.",
                "inference": "The plan may remain workable, but vehicle access is not established.",
                "consequence": "Trucks could arrive without a usable loading route, delaying the first setup.",
                "recommended_action": "Confirm the loading route with the location contact before dispatch.",
                "confidence": "low",
                "sources": sources,
            }
        ],
        change_note=None,
    )


def _mandatory_search_request(
    prompt: str,
    *,
    production_plan: str | None = None,
    production_date: str | None = None,
    location_context: str | None = None,
) -> tuple[str, list[str]]:
    """Build the baseline Parallel request that every live run must execute."""
    compact_plan = " ".join((production_plan or prompt).split())
    compact_location = " ".join((location_context or "").split())
    target = compact_location or compact_plan[:160]
    date = production_date.strip() if production_date else "current"
    search_subject = f"{target} {date}".strip()
    objective = (
        "Find current, directly relevant evidence that could confirm or contradict "
        "the production plan's assumptions about location access, closures, public "
        f"events, transport, filming restrictions and weather. Target: {target}. "
        f"Production date: {date}."
    )
    queries = [
        f"{search_subject} closures access restrictions",
        f"{search_subject} public events transport disruption",
        f"{search_subject} opening hours filming permit vehicle access",
        f"{search_subject} weather warnings",
    ]
    return objective, queries


async def _run_agent_text(agent: Any, prompt: str, app_name: str = APP_NAME) -> str:
    runner = InMemoryRunner(app_name=app_name, agent=agent)
    user_id = f"web-{uuid.uuid4().hex[:12]}"
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            text_parts = [
                part.text for part in event.content.parts if getattr(part, "text", None)
            ]
            if text_parts and (
                event.is_final_response()
                if hasattr(event, "is_final_response")
                else True
            ):
                final_text = "\n".join(text_parts)
    if not final_text:
        raise RuntimeError("SetWatch agent completed without a final response")
    return final_text


async def run_setwatch(
    prompt: str,
    *,
    production_plan: str | None = None,
    production_date: str | None = None,
    location_context: str | None = None,
) -> RunOutcome:
    settings = get_settings()
    run_id = f"sw-{uuid.uuid4().hex[:16]}"
    trace_token = start_trace()
    try:
        if settings.demo_mode:
            result = _demo_result()
            traces = current_traces()
            validated = True
            integrity = "degraded"
        else:
            objective, search_queries = _mandatory_search_request(
                prompt,
                production_plan=production_plan,
                production_date=production_date,
                location_context=location_context,
            )
            evidence = parallel_live_search(objective, search_queries)
            evidence_json = json.dumps(evidence, ensure_ascii=False, default=str)
            evidence_prompt = (
                f"{prompt}\n\n"
                "MANDATORY PARALLEL EVIDENCE\n"
                "This evidence packet was retrieved live by the SetWatch runtime. "
                "Use only supported claims, distinguish evidence from inference, and "
                "cite only source URLs present in this packet or in any additional "
                f"Parallel tool result.\n{evidence_json}"
            )
            final_text = await _run_agent_text(root_agent, evidence_prompt)

            traces = current_traces()
            live_traces = [t for t in traces if t.get("mode") == "LIVE_PARALLEL_SEARCH"]
            if not live_traces:
                raise RuntimeError("Qualifying run completed without a live Parallel Search trace")
            result, validated, integrity = _validated_result(final_text, traces)

        typed_traces = [PartnerTrace.model_validate(trace) for trace in traces]
        meta = RunMeta(
            mode="demo" if settings.demo_mode else "live",
            run_id=run_id,
            output_validated=validated,
            evidence_integrity=integrity,
            partner_search_count=len(typed_traces),
            partner_traces=typed_traces,
        )
        return RunOutcome(result=result, meta=meta)
    finally:
        close_trace(trace_token)
