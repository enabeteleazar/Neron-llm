from pydantic import BaseModel


class LLMRequest(BaseModel):
    message: str
    task: str | None = None
    mode: str | None = None  # "single" | "parallel" | "race"