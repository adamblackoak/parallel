from typing import Any

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    plan: str = Field(min_length=20, max_length=20_000)
    production_date: str | None = None
    location_context: str | None = None
    previous_snapshot: dict[str, Any] | None = None


class CheckResponse(BaseModel):
    result: dict[str, Any]
    meta: dict[str, Any]
