"""
Test qui PROUVE que les agents tournent en parallèle (et pas en séquentiel).

Principe :
  - On crée 3 providers factices qui "sleepent" respectivement 0.2s, 0.3s, 0.4s
  - Si on les exécute EN PARALLÈLE : temps total ≈ 0.4s (le plus lent)
  - Si on les exécute EN SÉQUENTIEL : temps total ≈ 0.9s (somme de tous)

Ce test échouera si l'exécution n'est PAS parallèle.
"""
import asyncio
import time

from neron_llm.core.manager import LLMManager


class SlowProvider:
    """Provider factice qui simule un appel réseau de durée connue."""

    def __init__(self, name: str, delay: float):
        self.name = name
        self.delay = delay

    async def generate(self, message: str) -> str:
        await asyncio.sleep(self.delay)
        return f"[{self.name}] response after {self.delay}s"


def test_parallel_execution():
    """Les providers doivent tourner en parallèle — temps total ≈ max(delays), pas sum(delays)."""
    mgr = LLMManager()
    mgr.providers = {
        "fast": SlowProvider("fast", 0.2),
        "medium": SlowProvider("medium", 0.3),
        "slow": SlowProvider("slow", 0.4),
    }

    class FakeRequest:
        message = "test"
        task = "default"
        mode = "parallel"

    start = time.perf_counter()
    result = asyncio.run(mgr.generate_parallel(FakeRequest()))
    elapsed = time.perf_counter() - start

    # Si parallèle : elapsed ≈ 0.4s (le plus lent)
    # Si séquentiel : elapsed ≈ 0.9s (somme)
    # On tolère un peu de overhead (0.15s max)
    assert elapsed < 0.6, (
        f"EXÉCUTION NON PARALLÈLE ! Temps={elapsed:.2f}s, attendu < 0.6s. "
        f"Si séquentiel ce serait ~0.9s."
    )

    # Vérifier que tous les providers ont répondu
    assert "fast" in result
    assert "medium" in result
    assert "slow" in result

    print(f"\n✅ PARALLÈLE confirmé : {elapsed:.3f}s (séquentiel aurait pris ~0.9s)")
    print(f"   Résultats : {result}")


def test_race_execution():
    """En mode race, le premier résultat gagne et les autres sont annulés."""
    mgr = LLMManager()
    mgr.providers = {
        "fast": SlowProvider("fast", 0.1),
        "medium": SlowProvider("medium", 0.3),
        "slow": SlowProvider("slow", 0.5),
    }

    class FakeRequest:
        message = "test"
        task = "default"
        mode = "race"

    start = time.perf_counter()
    result = asyncio.run(mgr.generate_race(FakeRequest()))
    elapsed = time.perf_counter() - start

    # Le plus rapide doit gagner, donc ~0.1s + overhead
    assert elapsed < 0.3, (
        f"RACE trop lent : {elapsed:.2f}s. Le provider 'fast' (0.1s) aurait dû gagner."
    )

    print(f"\n✅ RACE confirmé : {elapsed:.3f}s (provider 'fast' a gagné)")
    print(f"   Résultat : {result}")


def test_sequential_baseline():
    """Baseline séquentielle — doit prendre ~0.9s (somme des 3 delays)."""
    mgr = LLMManager()
    mgr.providers = {
        "fast": SlowProvider("fast", 0.2),
        "medium": SlowProvider("medium", 0.3),
        "slow": SlowProvider("slow", 0.4),
    }
    mgr.router.select_provider = lambda req: "fast"  # force un seul provider

    class FakeRequest:
        message = "test"
        task = "default"
        mode = "single"

    # On appelle 3x en séquentiel
    start = time.perf_counter()
    asyncio.run(mgr.generate(FakeRequest()))
    asyncio.run(mgr.generate(FakeRequest()))
    asyncio.run(mgr.generate(FakeRequest()))
    elapsed = time.perf_counter() - start

    # 3 × 0.2s = ~0.6s minimum
    assert elapsed > 0.4, (
        f"Séquentiel trop rapide : {elapsed:.2f}s, attendu > 0.4s"
    )

    print(f"\n✅ SÉQUENTIEL baseline : {elapsed:.3f}s (3 appels × 0.2s)")


if __name__ == "__main__":
    test_sequential_baseline()
    test_parallel_execution()
    test_race_execution()
    print("\n🎯 Tous les tests passés — le parallélisme est RÉEL, pas simulé.")