# core/models.py
from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str
    task: str | None = None
    context: dict = {}

class LLMResponse(BaseModel):
    text: str
    model: str
    provider: str
    latency: float
