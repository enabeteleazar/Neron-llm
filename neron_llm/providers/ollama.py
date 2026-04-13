import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral"


class OllamaProvider:

    def __init__(self, model: str = DEFAULT_MODEL, timeout: int = 60):
        self.model = model
        self.timeout = timeout

    async def generate(self, message: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": message,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")