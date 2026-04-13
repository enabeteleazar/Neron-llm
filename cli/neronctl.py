# cli/neronctl.py
import asyncio

import typer

from neron_llm.core.manager import LLMManager
from neron_llm.core.models import LLMRequest

app = typerTerminal = typer.Typer()
manager = LLMManager()


@app.command()
def launch(message: str, task: str = "default", mode: str = "single"):
    """Envoie un message au LLM.

    --mode: single (défaut), parallel (tous les providers), race (premier répondant)
    """
    req = LLMRequest(message=message, task=task, mode=mode)

    if mode == "parallel":
        result = asyncio.run(manager.generate_parallel(req))
    elif mode == "race":
        result = asyncio.run(manager.generate_race(req))
    else:
        result = asyncio.run(manager.generate(req))

    typer.echo(result)


if __name__ == "__main__":
    app()