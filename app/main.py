from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models import CheckRequest, CheckResponse
from app.runtime import run_setwatch

app = FastAPI(title="SetWatch", version="0.1.0")
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    settings = get_settings()
    missing = []
    if not settings.parallel_api_key:
        missing.append("PARALLEL_API_KEY")
    if not settings.google_cloud_project:
        missing.append("GOOGLE_CLOUD_PROJECT")
    return {
        "service": "setwatch",
        "status": "ok",
        "mode": "demo" if settings.demo_mode else "live",
        "parallel_configured": bool(settings.parallel_api_key),
        "google_cloud_project_configured": bool(settings.google_cloud_project),
        "live_ready": settings.live_ready,
        "missing_live_configuration": missing,
        "agent_framework": "google-adk",
        "model": settings.gemini_model,
    }


@app.post("/api/check", response_model=CheckResponse)
async def check_plan(request: CheckRequest) -> CheckResponse:
    settings = get_settings()
    if not settings.demo_mode and not settings.live_ready:
        missing = []
        if not settings.parallel_api_key:
            missing.append("PARALLEL_API_KEY")
        if not settings.google_cloud_project:
            missing.append("GOOGLE_CLOUD_PROJECT")
        raise HTTPException(
            status_code=503,
            detail=f"Live SetWatch is not configured: missing {', '.join(missing)}",
        )
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
        outcome = await run_setwatch(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {type(exc).__name__}: {exc}") from exc
    return CheckResponse(
        result=outcome.result,
        meta=outcome.meta,
    )
