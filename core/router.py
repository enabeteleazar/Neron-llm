# core/router.py
class LLMRouter:

    def select_provider(self, request):
        if request.task == "local":
            return "ollama"
        if request.task == "heavy":
            return "claude"
        return "ollama"

    def select_model(self, request):
        if request.task == "code":
            return "deepseek-coder"
        return "mistral"
