# cli/neronctl.py
import typer
import asyncio
from core.manager import LLMManager
from core.models import LLMRequest

app = typer.Typer()
manager = LLMManager()

@app.command()
def launch(prompt: str):
    req = LLMRequest(prompt=prompt)

    result = asyncio.run(manager.generate(req))
    print(result["text"])

if __name__ == "__main__":
    app()
