import asyncio
import httpx

# L'API Anthropic n'est pas async-native. On utilise httpx pour
# un vrai appel async HTTP plutôt que le SDK synchrone qui bloquerait
# l'event loop.

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class ClaudeProvider:

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model

    async def generate(self, message: str) -> str:
        if not self.api_key:
            # Fallback mock si pas de clé
            return f"[CLAUDE MOCK] {message}"

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": message}],
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]