class LLMRouter:

    # Mapping task → provider
    _TASK_PROVIDER = {
        "code": "claude",
        "default": "ollama",
    }

    # Mapping task → model
    _TASK_MODEL = {
        "code": "deepseek-coder",
        "default": "mistral",
    }

    # Provider(s) à exécuter en mode parallel/race
    _ALL_PROVIDERS = ["ollama", "claude"]

    def select_provider(self, request) -> str:
        task = request.task or "default"
        return self._TASK_PROVIDER.get(task, "ollama")

    def select_model(self, request) -> str:
        task = request.task or "default"
        return self._TASK_MODEL.get(task, "mistral")

    def select_all_providers(self) -> list[str]:
        """Retourne tous les providers disponibles pour exécution parallèle."""
        return list(self._ALL_PROVIDERS)