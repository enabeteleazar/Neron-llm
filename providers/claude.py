# providers/claude.py
import httpx

class ClaudeProvider:
    def __init__(self, api_key):
        self.api_key = api_key

    async def generate(self, prompt):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": self.api_key},
                json={
                    "model": "claude-3-sonnet",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return r.json()
