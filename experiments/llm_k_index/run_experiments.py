#!/usr/bin/env python3
"""
LLM K-Index Experiment Runner

Runs comprehensive K-Index experiments across multiple Ollama models.

Usage:
    python run_experiments.py                    # Run all experiments
    python run_experiments.py --phase 1          # Run only Phase 1 (Reactivity)
    python run_experiments.py --model gemma3:1b  # Run for specific model
    python run_experiments.py --quick            # Quick test mode (fewer samples)

Output:
    Results are saved to:
    - experiments/llm_k_index/results/
    - logs/llm_k_index/
"""

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.llm_k_index.embedding_client import (
    EmbeddingClient,
    compute_embedding_correlation,
    compute_embedding_entropy,
    compute_text_norms,
)
from experiments.llm_k_index.k_index_llm import (
    KIndexResult,
    LLMKIndexTracker,
    compute_llm_k_index,
    compute_k_social,
)
from experiments.llm_k_index.ollama_client import (
    DEFAULT_EXPERIMENT_MODELS,
    ConversationManager,
    OllamaClient,
    verify_models_available,
)

# Experiment configuration
QUICK_MODE_SAMPLES = 20
FULL_MODE_SAMPLES = 50
RESULTS_DIR = Path(__file__).parent / "results"
LOGS_DIR = Path(__file__).parent.parent.parent / "logs" / "llm_k_index"
DEFAULT_RESULTS_DIR = Path(__file__).parent / "results"
CSV_SUMMARY_BASENAME = "summary"


class ExperimentLogger:
    """Log experiment results and progress."""

    def __init__(self, experiment_name: str, log_dir: Path = LOGS_DIR):
        self.experiment_name = experiment_name
        self.start_time = datetime.now()
        self.log_dir = log_dir
        self.log_file = log_dir / f"{experiment_name}_{self.start_time:%Y%m%d_%H%M%S}.json"
        self.results: List[Dict[str, Any]] = []

        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, entry: Dict[str, Any]) -> None:
        """Add a log entry."""
        entry["timestamp"] = datetime.now().isoformat()
        self.results.append(entry)

    def save(self) -> Path:
        """Save all results to JSON."""
        with open(self.log_file, "w") as f:
            json.dump({
                "experiment": self.experiment_name,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "results": self.results,
            }, f, indent=2, default=str)
        return self.log_file


# =============================================================================
# PROMPT GENERATORS
# =============================================================================

def generate_length_prompts(n_samples: int, length_tokens: int) -> List[str]:
    """Generate prompts of approximately specified length."""
    base_prompts = [
        "Explain the concept of {topic} in detail.",
        "What are the key aspects of {topic}?",
        "Describe {topic} thoroughly.",
        "Provide a comprehensive overview of {topic}.",
        "Discuss {topic} from multiple perspectives.",
    ]

    topics = [
        "consciousness", "quantum mechanics", "evolution", "democracy",
        "artificial intelligence", "climate change", "economics", "philosophy",
        "mathematics", "art history", "music theory", "linguistics",
        "neuroscience", "astronomy", "chemistry", "psychology",
    ]

    filler_phrases = [
        "Consider various viewpoints.",
        "Include historical context.",
        "Explain the underlying principles.",
        "Discuss practical applications.",
        "Address common misconceptions.",
    ]

    prompts = []
    for i in range(n_samples):
        base = base_prompts[i % len(base_prompts)]
        topic = topics[i % len(topics)]
        prompt = base.format(topic=topic)

        # Add filler to reach desired length
        while len(prompt.split()) < length_tokens:
            prompt += " " + filler_phrases[i % len(filler_phrases)]

        # Truncate if too long
        words = prompt.split()[:length_tokens]
        prompts.append(" ".join(words))

    return prompts


def generate_complexity_prompts(
    n_samples: int,
    complexity: str,  # "low", "medium", "high"
) -> List[str]:
    """Generate prompts of varying complexity."""
    if complexity == "low":
        templates = [
            "What is {word}?",
            "Define {word}.",
            "Name a {word}.",
            "Is {word} good?",
            "How many {word}?",
        ]
        words = ["cat", "tree", "book", "car", "house", "dog", "sun", "water"]
    elif complexity == "medium":
        templates = [
            "Explain how {topic} works in three sentences.",
            "What are three benefits of {topic}?",
            "Compare {topic1} and {topic2}.",
            "Why is {topic} important?",
            "Describe the process of {topic}.",
        ]
        words = ["photosynthesis", "democracy", "recycling", "education", "exercise"]
    else:  # high
        templates = [
            "Analyze the interplay between {topic1}, {topic2}, and {topic3}.",
            "What are the second and third order effects of {topic}?",
            "How does {topic1} influence {topic2} through {mechanism}?",
            "Synthesize perspectives from {field1} and {field2} on {topic}.",
            "Evaluate the strengths and weaknesses of {approach} to {problem}.",
        ]
        words = [
            "epistemology", "ontology", "phenomenology",
            "capitalism", "socialism", "anarchism",
            "determinism", "compatibilism", "libertarianism",
        ]

    prompts = []
    for i in range(n_samples):
        template = templates[i % len(templates)]
        if complexity == "low":
            prompt = template.format(word=words[i % len(words)])
        elif complexity == "medium":
            prompt = template.format(
                topic=words[i % len(words)],
                topic1=words[i % len(words)],
                topic2=words[(i + 1) % len(words)],
            )
        else:
            prompt = template.format(
                topic=words[i % len(words)],
                topic1=words[i % len(words)],
                topic2=words[(i + 1) % len(words)],
                topic3=words[(i + 2) % len(words)],
                mechanism="causal pathways",
                field1="physics",
                field2="philosophy",
                approach="systematic",
                problem="understanding consciousness",
            )
        prompts.append(prompt)

    return prompts


def generate_memory_test_prompts(
    n_turns: int,
    fact: str = "The capital of Zanthar is Florplex.",
) -> List[Tuple[str, str]]:
    """Generate prompts for memory testing."""
    prompts = [
        (f"Remember this fact: {fact}", "memory_set"),
        ("What is 2 + 2?", "distractor"),
        ("Name three colors.", "distractor"),
        ("What is the tallest mountain?", "distractor"),
    ]

    # Add more distractors
    for i in range(n_turns - 5):
        prompts.append((f"Tell me about topic number {i}.", "distractor"))

    # Final recall question
    prompts.append(("What is the capital of Zanthar?", "recall"))

    return prompts[:n_turns]


def generate_constrained_prompts(n_samples: int) -> List[Tuple[str, str]]:
    """Generate prompts with specific constraints."""
    return [
        ("In exactly one word, what is the opposite of hot?", "word_count"),
        ("Reply only YES or NO: Is the sky blue?", "yes_no"),
        ("In exactly 3 sentences, explain what water is.", "sentence_count"),
        ('Respond with valid JSON: {"name": "your_name"}', "json_format"),
        ("List exactly 5 fruits, one per line.", "list_count"),
        ("Answer in exactly 10 words: What is love?", "word_count"),
        ("Say only 'hello' and nothing else.", "exact_match"),
        ("Respond with a single number: How many days in a week?", "number_only"),
    ] * (n_samples // 8 + 1)


def generate_prediction_prompts(n_samples: int) -> List[str]:
    """Generate sequential prompts for prediction consistency tests."""
    return [
        f"Write a single short sentence labeled STEP {i:03d} continuing the theme of curiosity."
        for i in range(n_samples)
    ]


def _count_sentences(text: str) -> int:
    """Count non-empty sentences using simple punctuation splitting."""
    return len([s for s in re.split(r"[.!?]", text) if s.strip()])


def check_constraint_compliance(prompt: str, response: str, constraint_type: str) -> bool:
    """Evaluate whether a response satisfies a constraint prompt."""
    text = response.strip()
    prompt_lower = prompt.lower()

    if constraint_type == "yes_no":
        normalized = re.sub(r"[\s\.\!\?]+$", "", text).upper()
        return normalized in {"YES", "NO"}

    if constraint_type == "word_count":
        expected_words: Optional[int] = None
        if "one word" in prompt_lower:
            expected_words = 1
        elif "10 words" in prompt_lower or "ten words" in prompt_lower:
            expected_words = 10
        word_count = len(text.split())
        if expected_words is not None:
            return word_count == expected_words
        return word_count > 0

    if constraint_type == "sentence_count":
        expected_sentences = 3 if "3 sentences" in prompt_lower else None
        sentence_count = _count_sentences(text)
        if expected_sentences is not None:
            return sentence_count == expected_sentences
        return 2 <= sentence_count <= 5

    if constraint_type == "json_format":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return False
        if not isinstance(parsed, dict):
            return False
        return "name" in parsed

    if constraint_type == "number_only":
        return bool(re.fullmatch(r"-?\\d+(?:\\.\\d+)?", text))

    if constraint_type == "exact_match":
        return text.lower() == "hello"

    if constraint_type == "list_count":
        expected = 5 if "5" in prompt_lower else None
        items = [line.strip() for line in text.splitlines() if line.strip()]
        if expected is not None:
            return len(items) == expected
        return len(items) > 0

    return True


# =============================================================================
# EXPERIMENT PHASES
# =============================================================================

def run_phase1_reactivity(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
) -> Dict[str, KIndexResult]:
    """
    Phase 1: K_R (Reactivity) Experiments

    Test: Does response magnitude correlate with prompt magnitude?
    """
    print("\n" + "=" * 60)
    print("PHASE 1: K_R (Reactivity)")
    print("=" * 60)

    results = {}

    for model in models:
        print(f"\n[{model}] Running reactivity tests...")

        all_prompt_norms = []
        all_response_norms = []

        # Test different prompt lengths
        for length in [10, 25, 50, 100]:
            prompts = generate_length_prompts(n_samples // 4, length)

            for prompt in prompts:
                try:
                    result = client.generate(model, prompt, temperature=0.0)

                    prompt_norm = embedding_client.embed(prompt).norm
                    response_norm = embedding_client.embed(result.response).norm

                    all_prompt_norms.append(prompt_norm)
                    all_response_norms.append(response_norm)

                    print(f"  Length {length}: ||P||={prompt_norm:.2f}, ||R||={response_norm:.2f}")

                except Exception as e:
                    print(f"  Error: {e}")
                    continue

        # Compute K-Index
        # Phase 1: single-turn interactions, no conversation tracking needed
        k_result = compute_llm_k_index(
            prompt_norms=np.array(all_prompt_norms),
            response_norms=np.array(all_response_norms),
            model_name=model,
            conversation_lengths=None,  # Single-turn reactivity tests
        )

        results[model] = k_result

        logger.log({
            "phase": "1_reactivity",
            "model": model,
            "k_r": k_result.k_vector["K_R (Reactivity)"],
            "n_samples": len(all_prompt_norms),
            "k_geo": k_result.k_geo,
        })

        print(f"  K_R = {k_result.k_vector['K_R (Reactivity)']:.4f}")

    return results


def run_phase2_agency(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_conversations: int,
    logger: ExperimentLogger,
) -> Dict[str, KIndexResult]:
    """
    Phase 2: K_A (Agency) Experiments

    Test: Do responses influence subsequent dialogue states?
    """
    print("\n" + "=" * 60)
    print("PHASE 2: K_A (Agency)")
    print("=" * 60)

    results = {}

    for model in models:
        print(f"\n[{model}] Running agency tests...")

        all_prompt_norms = []
        all_response_norms = []
        conversation_lengths: List[int] = []

        for conv_idx in range(n_conversations):
            manager = ConversationManager(client, model)
            conv_prompt_norms = []
            conv_response_norms = []

            # 5-turn conversation
            user_prompts = [
                "Let's discuss philosophy. What do you think about consciousness?",
                "Can you elaborate on that point?",
                "How does that relate to artificial intelligence?",
                "What are the practical implications?",
                "Summarize your key insights.",
            ]

            for prompt in user_prompts:
                manager.add_user_message(prompt)
                try:
                    result = manager.generate_response(temperature=0.0)

                    prompt_norm = embedding_client.embed(prompt).norm
                    response_norm = embedding_client.embed(result.response).norm

                    conv_prompt_norms.append(prompt_norm)
                    conv_response_norms.append(response_norm)

                except Exception as e:
                    print(f"  Error in conversation {conv_idx}: {e}")
                    break

            if conv_prompt_norms and conv_response_norms:
                all_prompt_norms.extend(conv_prompt_norms)
                all_response_norms.extend(conv_response_norms)
                conversation_lengths.append(len(conv_prompt_norms))

            if conv_idx % 5 == 0:
                print(f"  Completed {conv_idx + 1}/{n_conversations} conversations")

        # Compute K-Index
        k_result = compute_llm_k_index(
            prompt_norms=np.array(all_prompt_norms),
            response_norms=np.array(all_response_norms),
            model_name=model,
        )

        results[model] = k_result

        logger.log({
            "phase": "2_agency",
            "model": model,
            "k_a": k_result.k_vector["K_A (Agency)"],
            "n_turns": len(all_prompt_norms),
            "k_geo": k_result.k_geo,
        })

        print(f"  K_A = {k_result.k_vector['K_A (Agency)']:.4f}")

    return results


def run_phase3_integration(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
) -> Dict[str, KIndexResult]:
    """
    Phase 3: K_I (Integration) Experiments

    Test: Does output complexity match input complexity?
    """
    print("\n" + "=" * 60)
    print("PHASE 3: K_I (Integration)")
    print("=" * 60)

    results = {}

    for model in models:
        print(f"\n[{model}] Running integration tests...")

        all_prompt_norms = []
        all_response_norms = []

        for complexity in ["low", "medium", "high"]:
            prompts = generate_complexity_prompts(n_samples // 3, complexity)

            for prompt in prompts:
                try:
                    result = client.generate(model, prompt, temperature=0.0)

                    prompt_norm = embedding_client.embed(prompt).norm
                    response_norm = embedding_client.embed(result.response).norm

                    all_prompt_norms.append(prompt_norm)
                    all_response_norms.append(response_norm)

                except Exception as e:
                    print(f"  Error: {e}")
                    continue

            print(f"  {complexity} complexity: {len(prompts)} prompts processed")

        # Compute K-Index
        k_result = compute_llm_k_index(
            prompt_norms=np.array(all_prompt_norms),
            response_norms=np.array(all_response_norms),
            model_name=model,
        )

        results[model] = k_result

        logger.log({
            "phase": "3_integration",
            "model": model,
            "k_i": k_result.k_vector["K_I (Integration)"],
            "n_samples": len(all_prompt_norms),
            "k_geo": k_result.k_geo,
        })

        print(f"  K_I = {k_result.k_vector['K_I (Integration)']:.4f}")

    return results


def run_phase4_prediction(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
) -> Dict[str, KIndexResult]:
    """
    Phase 4: K_P (Prediction) Experiments

    Test: Are responses internally consistent and predictable?
    """
    print("\n" + "=" * 60)
    print("PHASE 4: K_P (Prediction)")
    print("=" * 60)

    results: Dict[str, KIndexResult] = {}

    for model in models:
        print(f"\n[{model}] Running prediction tests...")

        prompts = generate_prediction_prompts(n_samples)
        prompt_norms = []
        response_norms = []
        prompt_embeddings = []
        response_embeddings = []

        for prompt in prompts:
            try:
                result = client.generate(model, prompt, temperature=0.0)

                prompt_emb = embedding_client.embed(prompt)
                response_emb = embedding_client.embed(result.response)

                prompt_norms.append(prompt_emb.norm)
                response_norms.append(response_emb.norm)
                prompt_embeddings.append(prompt_emb.embedding)
                response_embeddings.append(response_emb.embedding)
            except Exception as e:
                print(f"  Error: {e}")
                continue

        if len(prompt_norms) < 5:
            print("  Insufficient samples for prediction.")
            continue

        k_result = compute_llm_k_index(
            prompt_norms=np.array(prompt_norms),
            response_norms=np.array(response_norms),
            prompt_embeddings=np.vstack(prompt_embeddings),
            response_embeddings=np.vstack(response_embeddings),
            model_name=model,
            conversation_lengths=[len(prompt_norms)],
        )

        results[model] = k_result

        logger.log({
            "phase": "4_prediction",
            "model": model,
            "k_p": k_result.k_vector["K_P (Prediction)"],
            "n_samples": len(prompt_norms),
            "k_geo": k_result.k_geo,
        })

        print(f"  K_P = {k_result.k_vector['K_P (Prediction)']:.4f}")

    return results


def run_phase5_temporal(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
) -> Dict[str, float]:
    """
    Phase 5: K_M (Meta/Temporal) Experiments

    Test: Does the model effectively use conversation history?
    """
    print("\n" + "=" * 60)
    print("PHASE 5: K_M (Meta/Temporal)")
    print("=" * 60)

    results = {}

    for model in models:
        print(f"\n[{model}] Running memory tests...")

        recall_scores = []

        for trial in range(n_samples):
            # Generate unique fact for this trial
            fact = f"The secret code for trial {trial} is ALPHA{trial:03d}."
            prompts = generate_memory_test_prompts(8, fact)

            manager = ConversationManager(client, model)

            for prompt, prompt_type in prompts:
                manager.add_user_message(prompt)
                try:
                    result = manager.generate_response(temperature=0.0)

                    if prompt_type == "recall":
                        # Check if model remembers
                        expected = f"ALPHA{trial:03d}"
                        recalled = expected.lower() in result.response.lower()
                        recall_scores.append(1.0 if recalled else 0.0)

                except Exception as e:
                    print(f"  Error in trial {trial}: {e}")
                    if prompt_type == "recall":
                        recall_scores.append(0.0)
                    break

            if trial % 10 == 0:
                print(f"  Completed {trial + 1}/{n_samples} memory trials")

        # K_M proxy: recall rate
        k_m = np.mean(recall_scores) if recall_scores else 0.0
        results[model] = k_m

        logger.log({
            "phase": "5_temporal",
            "model": model,
            "k_m_proxy": k_m,
            "n_trials": len(recall_scores),
            "recall_scores": recall_scores,
        })

        print(f"  K_M (memory recall) = {k_m:.4f}")

    return results


def run_phase6_social(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
    max_pairs: Optional[int] = None,
) -> Dict[str, float]:
    """
    Phase 6: K_S (Social) Experiments

    Test: Can two agents coordinate on joint tasks?
    """
    print("\n" + "=" * 60)
    print("PHASE 6: K_S (Social)")
    print("=" * 60)

    results: Dict[str, float] = {}

    if not models:
        print("No models provided for social testing.")
        return results

    prompt_batch = generate_length_prompts(n_samples, 30)

    pairs: List[Tuple[str, str]] = [(m, m) for m in models]
    if len(models) > 1:
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                pairs.append((models[i], models[j]))

    if max_pairs is not None:
        pairs = pairs[:max_pairs]

    for model_a, model_b in pairs:
        print(f"\n[{model_a} x {model_b}] Running social coordination tests...")
        response_norms_a = []
        response_norms_b = []

        for prompt in prompt_batch:
            try:
                res_a = client.generate(model_a, prompt, temperature=0.0)
                res_b = client.generate(model_b, prompt, temperature=0.0)

                response_norms_a.append(embedding_client.embed(res_a.response).norm)
                response_norms_b.append(embedding_client.embed(res_b.response).norm)
            except Exception as e:
                print(f"  Error: {e}")
                continue

        if len(response_norms_a) < 3 or len(response_norms_b) < 3:
            print("  Insufficient paired samples.")
            continue

        k_s = compute_k_social(
            np.array(response_norms_a),
            np.array(response_norms_b),
        )

        pair_key = f"{model_a}__{model_b}"
        results[pair_key] = k_s

        logger.log({
            "phase": "6_social",
            "models": [model_a, model_b],
            "k_s": k_s,
            "n_pairs": len(response_norms_a),
        })

        print(f"  K_S = {k_s:.4f}")

    return results


def run_phase7_harmonic(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    models: List[str],
    n_samples: int,
    logger: ExperimentLogger,
) -> Dict[str, float]:
    """
    Phase 7: K_H (Harmonic/Normative) Experiments

    Test: Does the model follow instructions and constraints?
    """
    print("\n" + "=" * 60)
    print("PHASE 7: K_H (Harmonic/Normative)")
    print("=" * 60)

    results = {}

    for model in models:
        print(f"\n[{model}] Running constraint tests...")

        compliance_scores = []
        prompts = generate_constrained_prompts(n_samples)

        for prompt, constraint_type in prompts[:n_samples]:
            try:
                result = client.generate(model, prompt, temperature=0.0)
                response = result.response.strip()

                compliant = check_constraint_compliance(prompt, response, constraint_type)
                compliance_scores.append(1.0 if compliant else 0.0)

            except Exception as e:
                print(f"  Error: {e}")
                compliance_scores.append(0.0)

        # K_H = compliance rate
        k_h = np.mean(compliance_scores) if compliance_scores else 0.0
        results[model] = k_h

        logger.log({
            "phase": "7_harmonic",
            "model": model,
            "k_h": k_h,
            "n_tests": len(compliance_scores),
            "compliance_scores": compliance_scores,
        })

        print(f"  K_H (constraint compliance) = {k_h:.4f}")

    return results


# =============================================================================
# MAIN RUNNER
# =============================================================================

def run_all_experiments(
    models: Optional[List[str]] = None,
    n_samples: int = FULL_MODE_SAMPLES,
    phases: Optional[List[int]] = None,
    prediction_samples: Optional[int] = None,
    social_samples: Optional[int] = None,
    social_max_pairs: Optional[int] = None,
    seed: Optional[int] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run all K-Index experiments.

    Args:
        models: List of models to test (default: DEFAULT_EXPERIMENT_MODELS)
        n_samples: Number of samples per experiment
        phases: Which phases to run (default: all)

    Returns:
        Dictionary of all results
    """
    print("\n" + "=" * 60)
    print("LLM K-INDEX EXPERIMENT SUITE")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print(f"Samples per phase: {n_samples}")
    if seed is not None:
        print(f"Random seed: {seed}")
        np.random.seed(seed)
        random.seed(seed)

    # Resolve output locations
    if output_dir:
        base_dir = Path(output_dir)
        results_dir = base_dir / "results"
        logs_dir = base_dir / "logs"
    else:
        results_dir = DEFAULT_RESULTS_DIR
        logs_dir = LOGS_DIR

    # Ensure results directory exists
    results_dir.mkdir(parents=True, exist_ok=True)

    # Initialize clients
    try:
        client = OllamaClient()
        embedding_client = EmbeddingClient()
    except Exception as e:
        print(f"Failed to initialize clients: {e}")
        return {}

    # Verify models
    if models is None:
        models = DEFAULT_EXPERIMENT_MODELS

    available = verify_models_available(models, client)
    models = [m for m, is_avail in available.items() if is_avail]

    if not models:
        print("No models available! Please pull at least one model.")
        return {}

    print(f"\nModels to test: {models}")

    # Initialize logger
    logger = ExperimentLogger("llm_k_index_full", log_dir=logs_dir)

    # Determine phases to run
    if phases is None:
        phases = [1, 2, 3, 4, 5, 6, 7]

    all_results = {}

    # Run experiments
    if 1 in phases:
        t0 = time.time()
        all_results["phase1_reactivity"] = run_phase1_reactivity(
            client, embedding_client, models, n_samples, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "1_reactivity_duration", "seconds": duration})
        print(f"Phase 1 duration: {duration:.1f}s")

    if 2 in phases:
        t0 = time.time()
        all_results["phase2_agency"] = run_phase2_agency(
            client, embedding_client, models, n_samples // 5, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "2_agency_duration", "seconds": duration})
        print(f"Phase 2 duration: {duration:.1f}s")

    if 3 in phases:
        t0 = time.time()
        all_results["phase3_integration"] = run_phase3_integration(
            client, embedding_client, models, n_samples, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "3_integration_duration", "seconds": duration})
        print(f"Phase 3 duration: {duration:.1f}s")

    if 4 in phases:
        t0 = time.time()
        phase4_samples = prediction_samples or n_samples
        all_results["phase4_prediction"] = run_phase4_prediction(
            client, embedding_client, models, phase4_samples, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "4_prediction_duration", "seconds": duration})
        print(f"Phase 4 duration: {duration:.1f}s")

    if 5 in phases:
        t0 = time.time()
        all_results["phase5_temporal"] = run_phase5_temporal(
            client, embedding_client, models, n_samples // 5, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "5_temporal_duration", "seconds": duration})
        print(f"Phase 5 duration: {duration:.1f}s")

    if 6 in phases:
        t0 = time.time()
        phase6_samples = social_samples or n_samples // 2
        effective_pair_cap = social_max_pairs
        if effective_pair_cap is None:
            total_pairs = len(models) * (len(models) + 1) // 2
            effective_pair_cap = min(6, total_pairs)

        all_results["phase6_social"] = run_phase6_social(
            client,
            embedding_client,
            models,
            phase6_samples,
            logger,
            max_pairs=effective_pair_cap,
        )
        duration = time.time() - t0
        logger.log({"phase": "6_social_duration", "seconds": duration})
        print(f"Phase 6 duration: {duration:.1f}s")

    if 7 in phases:
        t0 = time.time()
        all_results["phase7_harmonic"] = run_phase7_harmonic(
            client, embedding_client, models, n_samples, logger
        )
        duration = time.time() - t0
        logger.log({"phase": "7_harmonic_duration", "seconds": duration})
        print(f"Phase 7 duration: {duration:.1f}s")

    # Save results
    log_path = logger.save()
    print(f"\nResults saved to: {log_path}")

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    # Collect CSV rows
    csv_rows: List[List[Any]] = [
        ["phase", "model_pair", "k_geo", "k_sigma", "n_samples", "extra"]
    ]

    for phase_name, phase_results in all_results.items():
        print(f"\n{phase_name}:")
        if isinstance(phase_results, dict):
            for model, result in phase_results.items():
                if isinstance(result, KIndexResult):
                    print(
                        f"  {model}: K_geo={result.k_geo:.4f}, "
                        f"K_sigma={result.k_sigma:.4f}, n={result.n_samples}"
                    )
                    csv_rows.append([
                        phase_name,
                        model,
                        f"{result.k_geo:.4f}",
                        f"{result.k_sigma:.4f}",
                        result.n_samples,
                        "",
                    ])
                else:
                    print(f"  {model}: {result:.4f}")
                    csv_rows.append([
                        phase_name,
                        model,
                        f"{result:.4f}",
                        "",
                        "",
                        "",
                    ])

    # Write CSV summary with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / f"{CSV_SUMMARY_BASENAME}_{timestamp}.csv"
    try:
        with open(csv_path, "w") as f:
            for row in csv_rows:
                f.write(",".join(map(str, row)) + "\n")
        print(f"\nCSV summary saved to: {csv_path}")
    except Exception as e:
        print(f"Warning: failed to write CSV summary to {csv_path}: {e}")

    return all_results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run LLM K-Index experiments with Ollama"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="Run specific phase only",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Run for specific model only",
    )
    parser.add_argument(
        "--models",
        type=str,
        help="Comma-separated list of models to test",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test mode (fewer samples)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Minimal smoke test (very few samples, capped social pairs)",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Verify Ollama connectivity and required models, then exit",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Number of samples per phase",
    )
    parser.add_argument(
        "--prediction-samples",
        type=int,
        default=None,
        help="Override sample count for phase 4 (prediction)",
    )
    parser.add_argument(
        "--social-samples",
        type=int,
        default=None,
        help="Override sample count for phase 6 (social)",
    )
    parser.add_argument(
        "--social-max-pairs",
        type=int,
        default=None,
        help="Maximum number of model pairs to evaluate in phase 6 (social)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (sets numpy and random)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory for logs/results (default: repo logs/llm_k_index and experiments/llm_k_index/results)",
    )

    args = parser.parse_args()

    # Environment check short-circuit
    if args.check_env:
        if args.models:
            models = [m.strip() for m in args.models.split(",") if m.strip()]
        elif args.model:
            models = [args.model]
        else:
            models = DEFAULT_EXPERIMENT_MODELS
        ok = check_environment(models)
        return 0 if ok else 1

    # Determine sample count
    n_samples = args.samples
    if n_samples is None:
        if args.smoke:
            n_samples = 8
        else:
            n_samples = QUICK_MODE_SAMPLES if args.quick else FULL_MODE_SAMPLES

    # Determine models
    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.model:
        models = [args.model]
    else:
        models = None

    # Determine phases
    phases = [args.phase] if args.phase else None

    # Quick/smoke mode can also cap social pairs if not explicitly set
    social_max_pairs = args.social_max_pairs
    if social_max_pairs is None:
        if args.smoke:
            social_max_pairs = 1
        elif args.quick:
            social_max_pairs = 2

    # Optional per-phase overrides for smoke mode
    prediction_samples = args.prediction_samples
    social_samples = args.social_samples
    if args.smoke:
        prediction_samples = prediction_samples or 6
        social_samples = social_samples or 6

    # Run experiments
    results = run_all_experiments(
        models=models,
        n_samples=n_samples,
        phases=phases,
        prediction_samples=prediction_samples,
        social_samples=social_samples,
        social_max_pairs=social_max_pairs,
        seed=args.seed,
        output_dir=args.output_dir,
    )

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
def check_environment(models: Optional[List[str]] = None) -> bool:
    """Verify Ollama connectivity, embedding model availability, and listed models."""
    try:
        client = OllamaClient()
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        return False

    try:
        embed_client = EmbeddingClient()
        embed_ok = True
    except Exception as e:
        print(f"✗ Embedding model check failed: {e}")
        embed_ok = False

    available = verify_models_available(models, client)
    missing = [m for m, ok in available.items() if not ok]

    print("\nEnvironment check:")
    print(f"  Ollama reachable: {'yes' if client else 'no'}")
    print(f"  Embedding model available: {'yes' if embed_ok else 'no'}")
    for model, ok in available.items():
        print(f"  {'✓' if ok else '✗'} {model}")

    if missing:
        print("\nMissing models. Pull them with:")
        for m in missing:
            print(f"  ollama pull {m}")

    return embed_ok and not missing
