from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

OperationalStatus = Literal["GO", "VERIFY", "CHANGE"]


class Source(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = None
    url: str
    publish_date: str | None = None


class Finding(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: OperationalStatus
    assumption: str
    evidence: str
    inference: str
    consequence: str
    recommended_action: str
    confidence: Literal["high", "medium", "low"]
    sources: list[Source] = Field(default_factory=list)


class SetWatchResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    overall_status: OperationalStatus
    summary: str
    assumptions_checked: int = Field(ge=0)
    findings: list[Finding] = Field(default_factory=list)
    change_note: str | None = None
    raw_response: str | None = None


class PartnerTrace(BaseModel):
    mode: Literal["LIVE_PARALLEL_SEARCH", "DEMO_NOT_LIVE"]
    search_id: str | None = None
    objective: str
    search_queries: list[str]
    result_count: int = Field(ge=0)
    sources: list[Source] = Field(default_factory=list)


class RunMeta(BaseModel):
    mode: Literal["demo", "live"]
    run_id: str
    partner_runtime: str = "Parallel Search API"
    agent_runtime: str = "Google ADK + Gemini"
    output_validated: bool
    evidence_integrity: Literal["verified", "degraded"]
    partner_search_count: int = Field(ge=0)
    partner_traces: list[PartnerTrace] = Field(default_factory=list)


class CheckRequest(BaseModel):
    plan: str = Field(min_length=20, max_length=20_000)
    production_date: str | None = None
    location_context: str | None = None
    previous_snapshot: dict[str, Any] | None = None


class CheckResponse(BaseModel):
    result: SetWatchResult
    meta: RunMeta
