"""
Unit tests for LLM K-Index experiment helpers.
"""

import numpy as np

from experiments.llm_k_index.k_index_llm import compute_k_agency, compute_k_meta
from experiments.llm_k_index.run_experiments import (
    check_constraint_compliance,
    run_phase4_prediction,
    run_phase6_social,
)
from experiments.llm_k_index.k_index_llm import LLMKIndexTracker


def test_compute_k_agency_respects_conversation_boundaries():
    """
    Cross-conversation jumps should not contaminate Δ||O|| correlations.
    """
    prompt_norms = np.array([1.0, 3.0, 6.0, 100.0])
    response_norms = np.array([20.0, 30.0, 45.0, 5.0])

    k_segmented = compute_k_agency(
        prompt_norms,
        response_norms,
        conversation_lengths=[3, 1],
    )
    k_flat = compute_k_agency(prompt_norms, response_norms)

    assert k_segmented > 0.95
    assert k_flat < k_segmented


def test_compute_k_meta_history_alignment():
    """
    History-aware model should outperform Markov when responses depend on past prompts.
    """
    history_len = 2
    prompt_norms = np.arange(0, 40, dtype=float)
    response_norms = np.zeros_like(prompt_norms)

    for i in range(history_len, len(prompt_norms)):
        response_norms[i] = prompt_norms[i - 1] + prompt_norms[i - 2]

    k_m = compute_k_meta(
        prompt_norms,
        response_norms,
        history_len=history_len,
        conversation_lengths=[len(prompt_norms)],
    )

    assert k_m > 0.8


def test_check_constraint_compliance_strictness():
    """Constraint checks should enforce exact formats and counts."""
    assert check_constraint_compliance(
        "Reply only YES or NO", "YES", "yes_no"
    )
    assert not check_constraint_compliance(
        "Reply only YES or NO", "Maybe", "yes_no"
    )

    assert check_constraint_compliance(
        "In exactly one word, what is the opposite of hot?", "cold", "word_count"
    )
    assert not check_constraint_compliance(
        "In exactly one word, what is the opposite of hot?", "very cold", "word_count"
    )

    three_sentence_reply = "First sentence. Second sentence! Third sentence?"
    assert check_constraint_compliance(
        "In exactly 3 sentences, explain what water is.", three_sentence_reply, "sentence_count"
    )
    assert not check_constraint_compliance(
        "In exactly 3 sentences, explain what water is.", "Only one sentence.", "sentence_count"
    )

    assert check_constraint_compliance(
        'Respond with valid JSON: {"name": "your_name"}',
        '{"name": "alex"}',
        "json_format",
    )
    assert not check_constraint_compliance(
        'Respond with valid JSON: {"name": "your_name"}',
        '{"value": "alex"}',
        "json_format",
    )

    assert check_constraint_compliance(
        "Respond with a single number: How many days in a week?", "7", "number_only"
    )
    assert not check_constraint_compliance(
        "Respond with a single number: How many days in a week?", "seven", "number_only"
    )

    assert check_constraint_compliance("Say only 'hello' and nothing else.", "hello", "exact_match")
    assert not check_constraint_compliance(
        "Say only 'hello' and nothing else.", "hello there", "exact_match"
    )

    list_prompt = "List exactly 5 fruits, one per line."
    good_list = "apple\nbanana\ncherry\ndate\nelderberry"
    bad_list = "apple\nbanana\ncherry\ndate"
    assert check_constraint_compliance(list_prompt, good_list, "list_count")
    assert not check_constraint_compliance(list_prompt, bad_list, "list_count")


class _FakeEmbeddingResult:
    def __init__(self, text: str):
        val = float(len(text))
        # Simple 2D embedding tied to text length
        self.embedding = np.array([val, val + 1.0], dtype=np.float32)
        self.norm = float(np.linalg.norm(self.embedding))


class _FakeEmbeddingClient:
    def embed(self, text: str):
        return _FakeEmbeddingResult(text)


class _FakeGenerationResult:
    def __init__(self, response: str):
        self.response = response


class _FakeOllamaClient:
    def generate(self, model: str, prompt: str, temperature: float = 0.0):
        # Response length scales with prompt length and model name to induce correlation
        padding = "-" * (len(model) % 3)
        return _FakeGenerationResult(f"{prompt} :: response {padding}")


class _DummyLogger:
    def __init__(self):
        self.entries = []

    def log(self, entry):
        self.entries.append(entry)


def test_run_phase4_prediction_stubbed_clients():
    """Prediction phase produces non-zero K_P with deterministic fake clients."""
    client = _FakeOllamaClient()
    embedding_client = _FakeEmbeddingClient()
    logger = _DummyLogger()

    results = run_phase4_prediction(
        client=client,
        embedding_client=embedding_client,
        models=["model_a"],
        n_samples=12,
        logger=logger,
    )

    assert "model_a" in results
    assert results["model_a"].k_vector["K_P (Prediction)"] > 0.0


def test_run_phase6_social_stubbed_clients():
    """Social phase computes K_S for paired fake models."""
    client = _FakeOllamaClient()
    embedding_client = _FakeEmbeddingClient()
    logger = _DummyLogger()

    results = run_phase6_social(
        client=client,
        embedding_client=embedding_client,
        models=["model_a", "model_b"],
        n_samples=6,
        logger=logger,
    )

    assert "model_a__model_b" in results
    assert results["model_a__model_b"] > 0.0


def test_llm_k_index_tracker_conversation_boundaries():
    """Tracker propagates conversation lengths so K_A ignores cross-dialogue jumps."""
    client = _FakeEmbeddingClient()
    tracker = LLMKIndexTracker("fake_model", client)

    tracker.start_conversation()
    tracker.add_turn("p", "rr")          # len=1, 2
    tracker.add_turn("ppp", "rrrr")      # len=3, 4
    tracker.add_turn("pppppp", "rrrrrr") # len=6, 6

    tracker.start_conversation()
    tracker.add_turn("p" * 100, "s")     # large prompt jump, small response
    tracker.add_turn("p" * 101, "s")     # small delta within conversation

    result = tracker.compute()
    k_a = result.k_vector["K_A (Agency)"]

    assert k_a > 0.5
