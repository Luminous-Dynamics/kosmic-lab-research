#!/usr/bin/env python3
"""
Offline self-check for LLM K-Index helpers.

Runs small, deterministic checks without hitting Ollama/embedding services.
"""

import sys
from typing import Any, Dict, List

try:
    import numpy as np
except ImportError as e:  # pragma: no cover
    print("numpy is required for the self-check. Please install project dependencies.")
    sys.exit(1)

from experiments.llm_k_index.k_index_llm import LLMKIndexTracker
from experiments.llm_k_index.run_experiments import (
    check_constraint_compliance,
    run_phase4_prediction,
    run_phase6_social,
)


class _FakeEmbeddingResult:
    def __init__(self, text: str):
        val = float(len(text))
        self.embedding = np.array([val, val + 1.0], dtype=np.float32)
        self.norm = float(np.linalg.norm(self.embedding))


class _FakeEmbeddingClient:
    def embed(self, text: str) -> _FakeEmbeddingResult:
        return _FakeEmbeddingResult(text)


class _FakeGenerationResult:
    def __init__(self, response: str):
        self.response = response


class _FakeOllamaClient:
    def generate(self, model: str, prompt: str, temperature: float = 0.0) -> _FakeGenerationResult:
        padding = "-" * (len(model) % 3)
        return _FakeGenerationResult(f"{prompt} :: response {padding}")


class _DummyLogger:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def log(self, entry: Dict[str, Any]) -> None:
        self.entries.append(entry)


def _check_constraints() -> None:
    assert check_constraint_compliance("Reply only YES or NO", "YES", "yes_no")
    assert not check_constraint_compliance("Reply only YES or NO", "Maybe", "yes_no")
    assert check_constraint_compliance("In exactly one word, what is the opposite of hot?", "cold", "word_count")
    assert not check_constraint_compliance("In exactly one word, what is the opposite of hot?", "very cold", "word_count")


def _check_prediction() -> None:
    client = _FakeOllamaClient()
    embedding_client = _FakeEmbeddingClient()
    logger = _DummyLogger()

    results = run_phase4_prediction(
        client=client,
        embedding_client=embedding_client,
        models=["model_a"],
        n_samples=8,
        logger=logger,
    )
    assert "model_a" in results
    assert results["model_a"].k_vector["K_P (Prediction)"] > 0.0


def _check_social() -> None:
    client = _FakeOllamaClient()
    embedding_client = _FakeEmbeddingClient()
    logger = _DummyLogger()

    results = run_phase6_social(
        client=client,
        embedding_client=embedding_client,
        models=["model_a", "model_b"],
        n_samples=4,
        logger=logger,
        max_pairs=1,
    )
    assert "model_a__model_b" in results
    assert results["model_a__model_b"] > 0.0


def _check_tracker() -> None:
    client = _FakeEmbeddingClient()
    tracker = LLMKIndexTracker("fake_model", client)

    tracker.start_conversation()
    tracker.add_turn("p", "rr")
    tracker.add_turn("ppp", "rrrr")
    tracker.add_turn("pppppp", "rrrrrr")

    tracker.start_conversation()
    tracker.add_turn("p" * 100, "s")
    tracker.add_turn("p" * 101, "s")

    result = tracker.compute()
    assert result.k_vector["K_A (Agency)"] > 0.5


def main() -> int:
    try:
        _check_constraints()
        _check_prediction()
        _check_social()
        _check_tracker()
        print("✓ LLM K-Index self-check passed")
        return 0
    except AssertionError as e:
        print(f"✗ Self-check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
