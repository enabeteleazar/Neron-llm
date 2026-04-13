import asyncio
from typing import Any

from neron_llm.core.router import LLMRouter
from neron_llm.providers.ollama import OllamaProvider
from neron_llm.providers.claude import ClaudeProvider

# Timeout global pour chaque appel provider (en secondes)
PROVIDER_TIMEOUT = 60


class LLMManager:

    def __init__(self):
        self.router = LLMRouter()
        self.providers = {
            "ollama": OllamaProvider(),
            "claude": ClaudeProvider(),
        }

    async def generate(self, request) -> dict[str, Any]:
        """Exécution séquentielle d'un seul provider (comportement original)."""
        provider_name = self.router.select_provider(request)
        provider = self.providers[provider_name]

        try:
            result = await asyncio.wait_for(
                provider.generate(request.message),
                timeout=PROVIDER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            return {"provider": provider_name, "response": None, "error": "timeout"}
        except Exception as exc:
            return {"provider": provider_name, "response": None, "error": str(exc)}

        return {"provider": provider_name, "response": result}

    async def generate_parallel(self, request) -> dict[str, Any]:
        """Exécute TOUS les providers en parallèle et agrège les résultats.

        Chaque provider tourne dans sa propre coroutine. Le retour
        est disponible dès que tous ont répondu (ou timed out).
        """
        tasks = {
            name: asyncio.create_task(
                self._call_provider(name, provider, request.message),
            )
            for name, provider in self.providers.items()
        }

        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as exc:
                results[name] = {"response": None, "error": str(exc)}

        return results

    async def generate_race(self, request) -> dict[str, Any]:
        """Exécute tous les providers en parallèle et retourne le PREMIER résultat.

        Les autres sont annulés automatiquement (cancel-on-success).
        Utile pour réduire la latence perçue.
        """
        tasks = {}
        for name, provider in self.providers.items():
            tasks[name] = asyncio.create_task(
                self._call_provider(name, provider, request.message),
            )

        # as_completed manuel : on yield au premier résultat
        for coro in asyncio.as_completed(tasks.values()):
            try:
                result = await coro
                # Annuler les tâches restantes
                for t in tasks.values():
                    t.cancel()
                return result
            except Exception:
                continue

        return {"provider": None, "response": None, "error": "all providers failed"}

    # ------------------------------------------------------------------ #
    #  Helpers privés                                                      #
    # ------------------------------------------------------------------ #

    async def _call_provider(self, name: str, provider, message: str) -> dict:
        """Appelle un provider avec timeout et isolation d'erreur."""
        try:
            response = await asyncio.wait_for(
                provider.generate(message),
                timeout=PROVIDER_TIMEOUT,
            )
        except asyncio.TimeoutError:
            return {"provider": name, "response": None, "error": "timeout"}
        except Exception as exc:
            return {"provider": name, "response": None, "error": str(exc)}

        return {"provider": name, "response": response}