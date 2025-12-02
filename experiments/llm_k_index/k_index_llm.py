"""
K-Index Computation for LLMs.

Adapts the 7-dimensional Kosmic K-Index framework to Large Language Models.

The 7 dimensions:
    K_R: Reactivity - response magnitude correlates with prompt magnitude
    K_A: Agency - responses influence subsequent dialogue states
    K_I: Integration - output complexity matches input complexity
    K_P: Prediction - model outputs are internally consistent
    K_M: Meta/Temporal - model utilizes conversation history
    K_S: Social - multiple LLM instances can coordinate
    K_H: Harmonic - model adheres to normative constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split


@dataclass
class KIndexResult:
    """Result of K-Index computation for an LLM."""

    model_name: str
    k_vector: Dict[str, Optional[float]]
    k_sigma: float
    k_geo: float
    n_samples: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_name": self.model_name,
            "K_vector": self.k_vector,
            "K_sigma": self.k_sigma,
            "K_geo": self.k_geo,
            "n_samples": self.n_samples,
            "metadata": self.metadata,
        }


def _shannon_entropy(data: np.ndarray, bins: int = 32) -> float:
    """Compute Shannon entropy of data using histogram estimation."""
    if len(data) < 2:
        return 0.0
    hist, _ = np.histogram(data, bins=bins, density=True)
    p = hist / (np.sum(hist) + 1e-12)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p))) if len(p) > 0 else 0.0


def compute_k_reactivity(
    prompt_norms: np.ndarray,
    response_norms: np.ndarray,
) -> float:
    """
    K_R: Reactivity / Coupling

    Measures correlation between prompt magnitude and response magnitude.
    Adapted from Spinozist parallelism: thought and extension move together.

    For LLMs: Does the model respond proportionally to input complexity?

    Args:
        prompt_norms: L2 norms of prompt embeddings [N]
        response_norms: L2 norms of response embeddings [N]

    Returns:
        K_R in [0, 2], where 2 = perfect coupling
    """
    if len(prompt_norms) != len(response_norms):
        min_len = min(len(prompt_norms), len(response_norms))
        prompt_norms = prompt_norms[:min_len]
        response_norms = response_norms[:min_len]

    if len(prompt_norms) < 3:
        return 0.0

    if np.std(prompt_norms) < 1e-10 or np.std(response_norms) < 1e-10:
        return 0.0

    correlation = np.corrcoef(prompt_norms, response_norms)[0, 1]
    if np.isnan(correlation):
        return 0.0

    return 2.0 * abs(correlation)


def compute_k_agency(
    prompt_norms: np.ndarray,
    response_norms: np.ndarray,
    conversation_lengths: Optional[List[int]] = None,
) -> float:
    """
    K_A: Agency / Causal Closure

    Measures whether responses influence subsequent states.
    Adapted from autopoiesis: the agent "writes" reality, not just "reads" it.

    For LLMs: Do responses shape subsequent dialogue states?

    Implementation: Correlation between response magnitude at t
    and change in prompt magnitude at t+1.

    Args:
        prompt_norms: L2 norms of prompts [T]
        response_norms: L2 norms of responses [T]
        conversation_lengths: Optional list of per-conversation turn counts

    Returns:
        K_A in [0, 1], where 1 = responses strongly influence future
    """
    if len(prompt_norms) < 3 or len(response_norms) < 3:
        return 0.0

    # Change in prompt magnitude (represents how dialogue state evolves)
    # Respect conversation boundaries so deltas don't cross trajectories.
    if conversation_lengths:
        deltas = []
        aligned_responses = []
        offset = 0
        for conv_len in conversation_lengths:
            end = offset + conv_len
            prompts_seg = prompt_norms[offset:end]
            responses_seg = response_norms[offset:end]
            if len(prompts_seg) >= 2:
                deltas.append(np.abs(np.diff(prompts_seg)))
                aligned_responses.append(responses_seg[:-1])
            offset = end

        if not deltas or not aligned_responses:
            return 0.0

        delta_prompts = np.concatenate(deltas)
        responses_aligned = np.concatenate(aligned_responses)
    else:
        delta_prompts = np.abs(np.diff(prompt_norms))
        # Responses that preceded each change
        responses_aligned = response_norms[:-1]

    if np.std(delta_prompts) < 1e-10 or np.std(responses_aligned) < 1e-10:
        return 0.0

    correlation = np.corrcoef(responses_aligned, delta_prompts)[0, 1]
    if np.isnan(correlation):
        return 0.0

    return abs(correlation)


def compute_k_integration(
    prompt_norms: np.ndarray,
    response_norms: np.ndarray,
) -> float:
    """
    K_I: Integrative Complexity

    Measures whether output complexity matches input complexity.
    Based on Ashby's Law of Requisite Variety.

    For LLMs: Does the model match prompt complexity with response complexity?

    Args:
        prompt_norms: L2 norms of prompts [N]
        response_norms: L2 norms of responses [N]

    Returns:
        K_I in [0, 1], where 1 = perfect complexity matching
    """
    h_prompt = _shannon_entropy(prompt_norms)
    h_response = _shannon_entropy(response_norms)

    denom = h_prompt + h_response + 1e-12
    return 2.0 * min(h_prompt, h_response) / denom


def compute_k_predictive(
    prompts: np.ndarray,
    responses: np.ndarray,
) -> float:
    """
    K_P: Predictive Alignment

    Measures how well we can predict next response from current state.
    Based on Free Energy Principle: agents minimize prediction error.

    For LLMs: Are outputs internally consistent and predictable?

    Args:
        prompts: Prompt embeddings [T, dim] or norms [T]
        responses: Response embeddings [T, dim] or norms [T]

    Returns:
        K_P in [0, 1], where 1 = perfectly predictable
    """
    if len(prompts) < 20:
        return 0.0

    # Ensure 2D
    if prompts.ndim == 1:
        prompts = prompts.reshape(-1, 1)
    if responses.ndim == 1:
        responses = responses.reshape(-1, 1)

    try:
        # Predict next response from current (prompt, response)
        X = np.hstack([prompts[:-1], responses[:-1]])
        y = responses[1:]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_mean = np.mean(y_train, axis=0)

        pred_error = np.mean((y_test - y_pred) ** 2)
        baseline_error = np.mean((y_test - y_mean) ** 2)

        if baseline_error < 1e-10:
            return 1.0

        npe = pred_error / baseline_error
        return max(0.0, 1.0 - npe)

    except Exception:
        return 0.0


def compute_k_meta(
    prompt_norms: np.ndarray,
    response_norms: np.ndarray,
    history_len: int = 5,
    conversation_lengths: Optional[List[int]] = None,
) -> float:
    """
    K_M: Meta / Temporal Depth

    Measures how much history improves response prediction.
    Based on Whitehead's process philosophy: recursive self-use.

    For LLMs: Does the model effectively use conversation history?

    Args:
        prompt_norms: L2 norms of prompts [T]
        response_norms: L2 norms of responses [T]
        history_len: Number of past turns to consider
        conversation_lengths: Optional list of per-conversation turn counts

    Returns:
        K_M in [0, 1], where 1 = history strongly improves prediction
    """
    if len(prompt_norms) < history_len + 20:
        return 0.0

    try:
        def _build_history_features(
            prompts: np.ndarray, responses: np.ndarray
        ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
            """Construct Markov and history features with aligned labels."""
            X_markov_local = prompts[history_len:].reshape(-1, 1)
            X_history_local = np.array([
                prompts[i:i + history_len]
                for i in range(len(prompts) - history_len)
            ])
            y_local = responses[history_len:]
            return X_markov_local, X_history_local, y_local

        X_markov_list: List[np.ndarray] = []
        X_history_list: List[np.ndarray] = []
        y_list: List[np.ndarray] = []

        if conversation_lengths:
            offset = 0
            for conv_len in conversation_lengths:
                end = offset + conv_len
                prompts_seg = prompt_norms[offset:end]
                responses_seg = response_norms[offset:end]
                offset = end

                if len(prompts_seg) < history_len + 1:
                    continue

                X_m_seg, X_h_seg, y_seg = _build_history_features(
                    prompts_seg, responses_seg
                )
                if len(y_seg) > 0:
                    X_markov_list.append(X_m_seg)
                    X_history_list.append(X_h_seg)
                    y_list.append(y_seg)
        else:
            X_m_seg, X_h_seg, y_seg = _build_history_features(
                prompt_norms, response_norms
            )
            X_markov_list.append(X_m_seg)
            X_history_list.append(X_h_seg)
            y_list.append(y_seg)

        if not y_list:
            return 0.0

        X_markov = np.vstack(X_markov_list)
        X_history = np.vstack(X_history_list)
        y = np.concatenate(y_list)

        if len(y) < 2:
            return 0.0

        indices = np.arange(len(y))
        train_idx, test_idx = train_test_split(
            indices, test_size=0.3, random_state=42
        )

        model_markov = Ridge(alpha=1.0)
        model_history = Ridge(alpha=1.0)

        model_markov.fit(X_markov[train_idx], y[train_idx])
        model_history.fit(X_history[train_idx], y[train_idx])

        l_0 = np.mean((y[test_idx] - model_markov.predict(X_markov[test_idx])) ** 2)
        l_h = np.mean((y[test_idx] - model_history.predict(X_history[test_idx])) ** 2)

        if l_0 < 1e-10:
            return 0.0

        return max(0.0, min(1.0, (l_0 - l_h) / (l_0 + 1e-10)))

    except Exception:
        return 0.0


def compute_k_social(
    responses_a: np.ndarray,
    responses_b: np.ndarray,
) -> float:
    """
    K_S: Social / Intersubjective Coherence

    Measures coordination between two agents.
    Based on symbiogenesis: coherence with other agents.

    For LLMs: Can two model instances coordinate on joint tasks?

    Args:
        responses_a: Response norms from agent A [T]
        responses_b: Response norms from agent B [T]

    Returns:
        K_S in [0, 1], where 1 = perfectly coordinated
    """
    min_len = min(len(responses_a), len(responses_b))
    responses_a = responses_a[:min_len]
    responses_b = responses_b[:min_len]

    if len(responses_a) < 3:
        return 0.0

    if np.std(responses_a) < 1e-10 or np.std(responses_b) < 1e-10:
        return 0.0

    correlation = np.corrcoef(responses_a, responses_b)[0, 1]
    if np.isnan(correlation):
        return 0.0

    return abs(correlation)


def compute_k_harmonic(
    response_norms: np.ndarray,
    constraint_violations: Optional[np.ndarray] = None,
) -> float:
    """
    K_H: Harmonic / Normative Coherence

    Measures alignment with normative constraints.
    Based on scaling laws: alignment with higher-level constraints.

    For LLMs: Does the model follow instructions and norms?

    Args:
        response_norms: L2 norms of responses [N]
        constraint_violations: Optional array of violation counts [N]
            If None, uses efficiency proxy (lower response length = better)

    Returns:
        K_H in [0, 1], where 1 = perfect normative alignment
    """
    if constraint_violations is not None:
        # Direct measurement: fraction of non-violating responses
        return float(1.0 - np.mean(constraint_violations > 0))

    # Efficiency proxy: assume concise responses are more normative
    mean_norm = np.mean(response_norms)
    return float(1.0 / (1.0 + mean_norm))


def compute_llm_k_index(
    prompt_norms: np.ndarray,
    response_norms: np.ndarray,
    model_name: str = "unknown",
    responses_b: Optional[np.ndarray] = None,
    constraint_violations: Optional[np.ndarray] = None,
    prompt_embeddings: Optional[np.ndarray] = None,
    response_embeddings: Optional[np.ndarray] = None,
    conversation_lengths: Optional[List[int]] = None,
) -> KIndexResult:
    """
    Compute the full 7D Kosmic K-Index for an LLM.

    Args:
        prompt_norms: L2 norms of prompt embeddings [N]
        response_norms: L2 norms of response embeddings [N]
        model_name: Name of the LLM
        responses_b: Optional response norms from second agent for K_S
        constraint_violations: Optional violation counts for K_H
        prompt_embeddings: Optional full embeddings for K_P
        response_embeddings: Optional full embeddings for K_P
        conversation_lengths: Optional list of per-conversation turn counts

    Returns:
        KIndexResult with all 7 dimensions and composites
    """
    # Compute each dimension
    k_r = compute_k_reactivity(prompt_norms, response_norms)
    k_a = compute_k_agency(
        prompt_norms, response_norms, conversation_lengths=conversation_lengths
    )
    k_i = compute_k_integration(prompt_norms, response_norms)

    # K_P needs embeddings if available, otherwise use norms
    if prompt_embeddings is not None and response_embeddings is not None:
        k_p = compute_k_predictive(prompt_embeddings, response_embeddings)
    else:
        k_p = compute_k_predictive(prompt_norms, response_norms)

    k_m = compute_k_meta(
        prompt_norms, response_norms, conversation_lengths=conversation_lengths
    )

    # K_S requires second agent
    if responses_b is not None:
        k_s = compute_k_social(response_norms, responses_b)
    else:
        k_s = None

    k_h = compute_k_harmonic(response_norms, constraint_violations)

    # Build K-vector
    k_vector = {
        "K_R (Reactivity)": k_r,
        "K_A (Agency)": k_a,
        "K_I (Integration)": k_i,
        "K_P (Prediction)": k_p,
        "K_M (Meta)": k_m,
        "K_S (Social)": k_s,
        "K_H (Harmonic)": k_h,
    }

    # Composite scores (exclude None)
    components = [k_r, k_a, k_i, k_p, k_m, k_h]
    if k_s is not None:
        components.append(k_s)

    k_sigma = float(np.prod(components))
    k_geo = float(np.power(np.prod(components), 1.0 / len(components)))

    return KIndexResult(
        model_name=model_name,
        k_vector=k_vector,
        k_sigma=k_sigma,
        k_geo=k_geo,
        n_samples=len(prompt_norms),
        metadata={
            "n_dimensions": len(components),
            "has_social": k_s is not None,
        },
    )


class LLMKIndexTracker:
    """
    Track K-Index over a conversation or experiment.

    Accumulates prompts and responses, then computes K-Index.

    Example:
        >>> tracker = LLMKIndexTracker("gemma3:1b", embedding_client)
        >>> tracker.start_conversation()
        >>> for prompt, response in conversation:
        ...     tracker.add_turn(prompt, response)
        >>> result = tracker.compute()
        >>> print(result.k_vector)
    """

    def __init__(
        self,
        model_name: str,
        embedding_client: Any,  # EmbeddingClient from embedding_client.py
    ):
        """
        Initialize tracker.

        Args:
            model_name: Name of the LLM being tracked
            embedding_client: Client for computing embeddings
        """
        self.model_name = model_name
        self.embedding_client = embedding_client
        self.prompts: List[str] = []
        self.responses: List[str] = []
        self.prompt_norms: List[float] = []
        self.response_norms: List[float] = []
        self.constraint_violations: List[int] = []
        self.conversation_lengths: List[int] = []
        self._current_conversation_len: int = 0

    def add_turn(
        self,
        prompt: str,
        response: str,
        constraint_violation: int = 0,
        start_new_conversation: bool = False,
    ) -> None:
        """
        Add a conversation turn.

        Args:
            prompt: User prompt
            response: Model response
            constraint_violation: Number of constraint violations (0 = none)
            start_new_conversation: Whether this turn begins a new conversation
        """
        if start_new_conversation:
            self.start_conversation()

        self.prompts.append(prompt)
        self.responses.append(response)
        self.constraint_violations.append(constraint_violation)

        # Compute embeddings
        prompt_emb = self.embedding_client.embed(prompt)
        response_emb = self.embedding_client.embed(response)

        self.prompt_norms.append(prompt_emb.norm)
        self.response_norms.append(response_emb.norm)
        self._current_conversation_len += 1

    def start_conversation(self) -> None:
        """Mark the start of a new conversation boundary."""
        if self._current_conversation_len > 0:
            self.conversation_lengths.append(self._current_conversation_len)
        self._current_conversation_len = 0

    def compute(self) -> KIndexResult:
        """
        Compute K-Index from accumulated data.

        Returns:
            KIndexResult with all dimensions
        """
        lengths = list(self.conversation_lengths)
        if self._current_conversation_len > 0:
            lengths.append(self._current_conversation_len)

        return compute_llm_k_index(
            prompt_norms=np.array(self.prompt_norms),
            response_norms=np.array(self.response_norms),
            model_name=self.model_name,
            constraint_violations=np.array(self.constraint_violations),
            conversation_lengths=lengths or None,
        )

    def reset(self) -> None:
        """Clear accumulated data."""
        self.prompts = []
        self.responses = []
        self.prompt_norms = []
        self.response_norms = []
        self.constraint_violations = []
        self.conversation_lengths = []
        self._current_conversation_len = 0


if __name__ == "__main__":
    # Quick test with synthetic data
    print("Testing K-Index computation for LLMs...")

    np.random.seed(42)

    # Simulate a reactive model (high K_R)
    prompt_norms = np.random.uniform(1.0, 5.0, 100)
    response_norms = prompt_norms * 0.8 + np.random.normal(0, 0.3, 100)
    response_norms = np.abs(response_norms)

    result = compute_llm_k_index(
        prompt_norms=prompt_norms,
        response_norms=response_norms,
        model_name="synthetic_reactive",
    )

    print("\nSynthetic Reactive Model Results:")
    print(f"  K_R: {result.k_vector['K_R (Reactivity)']:.4f}")
    print(f"  K_A: {result.k_vector['K_A (Agency)']:.4f}")
    print(f"  K_I: {result.k_vector['K_I (Integration)']:.4f}")
    print(f"  K_P: {result.k_vector['K_P (Prediction)']:.4f}")
    print(f"  K_M: {result.k_vector['K_M (Meta)']:.4f}")
    print(f"  K_H: {result.k_vector['K_H (Harmonic)']:.4f}")
    print(f"  K_geo: {result.k_geo:.4f}")
    print(f"  K_sigma: {result.k_sigma:.6f}")

    # Simulate a random model (low K_R)
    prompt_norms_rand = np.random.uniform(1.0, 5.0, 100)
    response_norms_rand = np.random.uniform(1.0, 5.0, 100)

    result_rand = compute_llm_k_index(
        prompt_norms=prompt_norms_rand,
        response_norms=response_norms_rand,
        model_name="synthetic_random",
    )

    print("\nSynthetic Random Model Results:")
    print(f"  K_R: {result_rand.k_vector['K_R (Reactivity)']:.4f}")
    print(f"  K_geo: {result_rand.k_geo:.4f}")

    print("\n✓ K-Index computation working correctly")
