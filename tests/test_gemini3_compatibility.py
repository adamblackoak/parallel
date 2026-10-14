"""Offline ADK history contract tests; these do not validate the Cloud service."""

import pytest
from google.adk import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import PrivateAttr

from app.agent import generation_config
from app.config import Settings
from app.runtime import _run_agent_text


def test_submission_default_and_candidate_override(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert Settings(_env_file=None).gemini_model == "gemini-2.5-flash"
    candidate = Settings(_env_file=".env.gemini3.example")
    assert candidate.gemini_model == "gemini-3.5-flash-lite"
    assert candidate.google_cloud_location == "global"


@pytest.mark.parametrize("model", ["gemini-3.5-flash-lite", "gemini-3.8-flash"])
@pytest.mark.parametrize("json_output", [False, True])
def test_gemini3_request_controls(model, json_output):
    config = generation_config(model, json_output=json_output)
    assert config.temperature is None
    assert config.seed is None
    assert config.top_p is None
    assert config.top_k is None
    assert config.thinking_config.thinking_level == "MEDIUM"
    assert config.thinking_config.thinking_budget is None
    assert config.response_mime_type == ("application/json" if json_output else None)


class SignedToolModel(BaseLlm):
    """Assert the actual ADK runner returns complete signed parts after tools."""

    _step: int = PrivateAttr(default=0)
    _signed_contents: list = PrivateAttr(default_factory=list)

    async def generate_content_async(self, llm_request, stream=False):
        assert llm_request.contents[-1].role != "model"
        if self._step:
            # Each earlier model step must survive, including signatures on an
            # empty text part and the first of two parallel calls.
            model_contents = [c for c in llm_request.contents if c.role == "model"]
            assert len(model_contents) == len(self._signed_contents)
            for actual, expected in zip(model_contents, self._signed_contents):
                assert actual.model_dump() == expected.model_dump()
            responses = [
                p.function_response
                for c in llm_request.contents
                for p in c.parts
                if p.function_response
            ]
            calls = [p.function_call for c in self._signed_contents for p in c.parts if p.function_call]
            assert [(r.id, r.name) for r in responses] == [(c.id, c.name) for c in calls]
        if self._step < 2:
            step = self._step
            content = types.Content(role="model", parts=[
                types.Part(text="", thought=True, thought_signature=b"empty-signature"),
                types.Part(function_call=types.FunctionCall(name="lookup", id=f"call-{step}-a", args={"subject": "access"}), thought_signature=f"signature-{step}".encode()),
                types.Part(function_call=types.FunctionCall(name="lookup", id=f"call-{step}-b", args={"subject": "transport"})),
            ])
            self._signed_contents.append(content.model_copy(deep=True))
            self._step += 1
            yield LlmResponse(content=content)
        else:
            yield LlmResponse(content=types.Content(role="model", parts=[
                types.Part(text="Internal summary must not enter result JSON", thought=True),
                types.Part(text='{"overall_status":"VERIFY"}', thought_signature=b"final-signature"),
            ]))


@pytest.mark.asyncio
async def test_adk_preserves_parallel_and_sequential_signatures_and_call_ids():
    def lookup(subject: str) -> dict:
        """Look up synthetic evidence for a subject."""
        return {"subject": subject, "status": "requires confirmation"}

    agent = Agent(name="signature_test", model=SignedToolModel(model="gemini-3.5-flash-lite"), tools=[lookup])
    assert await _run_agent_text(agent, "Check access and transport") == '{"overall_status":"VERIFY"}'


def test_sdk_serialization_preserves_signed_parts():
    content = types.Content(role="model", parts=[
        types.Part(text="", thought_signature=b"opaque-signature"),
        types.Part(function_call=types.FunctionCall(name="lookup", id="original-id", args={}), thought_signature=b"call-signature"),
    ])
    assert types.Content.model_validate_json(content.model_dump_json()) == content
