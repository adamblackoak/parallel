from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models import CheckRequest, CheckResponse
from app.runtime import run_setwatch

settings = get_settings()
app = FastAPI(title="SetWatch", version="0.1.0")
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    return {
        "service": "setwatch",
        "status": "ok",
        "mode": "demo" if settings.demo_mode else "live",
        "parallel_configured": bool(settings.parallel_api_key),
        "google_cloud_project_configured": bool(settings.google_cloud_project),
        "agent_framework": "google-adk",
        "model": settings.gemini_model,
    }


@app.post("/api/check", response_model=CheckResponse)
async def check_plan(request: CheckRequest) -> CheckResponse:
    context = {
        "production_date": request.production_date,
        "location_context": request.location_context,
        "previous_snapshot": request.previous_snapshot,
    }
    prompt = (
        "Run a SetWatch pre-flight check on the production plan below. "
        "Research material external assumptions with the Parallel Search tool before reaching conclusions.\n\n"
        f"CONTEXT\n{json.dumps(context, ensure_ascii=False, default=str)}\n\n"
        f"PRODUCTION PLAN\n{request.plan}"
    )

    try:
        result = await run_setwatch(prompt)
    except Exception as exc:  # surfaced cleanly to the web client; server logs retain exception details
        raise HTTPException(status_code=502, detail=f"Agent run failed: {type(exc).__name__}: {exc}") from exc

    return CheckResponse(
        result=result,
        meta={
            "mode": "demo" if settings.demo_mode else "live",
            "partner_runtime": "Parallel Search API",
            "agent_runtime": "Google ADK + Gemini",
        },
    )
