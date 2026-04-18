"""neron_llm/core/types.py
Data models for neron_llm — standardized request/response formats.

v2.0 additions:
  • GenerateRequest  — public bus contract (POST /llm/generate)
  • GenerateResponse — public bus contract response
  • Internal LLMRequest / LLMResponse unchanged for backward compat
"""
from __future__ import annotations

from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field


# ── Internal types (LLMManager / providers) ───────────────────────────────────

class LLMRequest(BaseModel):
    """Internal request passed through Manager → Provider pipeline."""

    message:  str
    task:     Optional[str]                              = Field(default=None)
    mode:     Optional[Literal["single", "parallel", "race"]] = Field(default=None)
    provider: Optional[str]                              = Field(default=None)
    model:    Optional[str]                              = Field(default=None)
    metadata: Optional[Dict[str, str]]                   = Field(default=None)


class LLMResponse(BaseModel):
    """Internal response from the Manager pipeline."""

    model:    str
    provider: str
    response: str
    error:    Optional[str] = None


# ── Public bus contract ───────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """Payload received at POST /llm/generate — the only external contract."""

    task_type:        Literal["code", "reasoning", "chat", "agent"] = Field(default="chat")
    prompt:           str
    context:          Dict[str, str]  = Field(default_factory=dict)
    model_preference: str             = Field(default="auto")
    request_id:       str             = Field(default="")


class GenerateResponse(BaseModel):
    """Response returned by POST /llm/generate."""

    result:     str
    model_used: str
    latency_ms: int
    warning:    Optional[str] = None
