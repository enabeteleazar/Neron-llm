# providers/ollama.py
import httpx
import asyncio

class OllamaProvider:
    def __init__(self):
        self.base_url = "http://localhost:11434"

    async def generate(self, prompt, model="mistral"):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt}
            )
            return r.json()["response"] 
