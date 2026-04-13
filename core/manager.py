# core/manager.py
import time
from core.router import LLMRouter
from providers.ollama import OllamaProvider
from providers.claude import ClaudeProvider

class LLMManager:

    def __init__(self):
        self.router = LLMRouter()
        self.providers = {
            "ollama": OllamaProvider(),
            "claude": ClaudeProvider(api_key="KEY")
        }

    async def generate(self, request):
        start = time.time()

        provider_name = self.router.select_provider(request)
        model = self.router.select_model(request)

        provider = self.providers[provider_name]

        result = await provider.generate(request.prompt)

        return {
            "text": result,
            "provider": provider_name,
            "model": model,
            "latency": time.time() - start
        }
