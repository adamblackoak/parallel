from __future__ import annotations

import json
import uuid
from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import root_agent

APP_NAME = "setwatch"


def _extract_json(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        if candidate.startswith("json"):
            candidate = candidate[4:].lstrip()
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(candidate[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return {
        "overall_status": "VERIFY",
        "summary": "The agent completed research but returned an unstructured response that requires review.",
        "assumptions_checked": 0,
        "findings": [],
        "change_note": None,
        "raw_response": text,
    }


async def run_setwatch(prompt: str) -> dict[str, Any]:
    runner = InMemoryRunner(app_name=APP_NAME, agent=root_agent)
    user_id = f"web-{uuid.uuid4().hex[:12]}"
    session = await runner.session_service.create_session(app_name=APP_NAME, user_id=user_id)
    message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            text_parts = [part.text for part in event.content.parts if getattr(part, "text", None)]
            if text_parts and (event.is_final_response() if hasattr(event, "is_final_response") else True):
                final_text = "\n".join(text_parts)

    if not final_text:
        raise RuntimeError("SetWatch agent completed without a final response")

    return _extract_json(final_text)
