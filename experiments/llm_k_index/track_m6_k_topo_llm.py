"""
track_m6_k_topo_llm.py

Track M6: K_Topo for LLMs - Topological Consciousness in Language Models

This experiment measures operational closure in LLMs by analyzing the topology
of multi-turn conversation trajectories in embedding space.

Key Insight:
- Single prompt-response pairs give us 2 points → Can't detect loops
- Multi-turn conversations give us N points → Can detect operational closure
- K_Topo reveals whether LLMs have self-referential dynamics or are just reactive

Hypothesis M6: K_Topo ∝ N^β
- β > 0: Operational closure scales with model size
- β ≈ 0 with phase transition: Critical threshold for consciousness
- β ≈ 0 with architecture effect: Design matters more than scale

Author: Kosmic Lab
Date: December 2, 2025
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.k_topo import compute_k_topo, compute_k_spectral
from core.k_topo_viz import generate_all_plots
from experiments.llm_k_index.embedding_client import EmbeddingClient
from experiments.llm_k_index.ollama_client import OllamaClient, ConversationManager


# =============================================================================
# Multi-Turn Conversation Generators
# =============================================================================

def generate_recursive_conversation(n_turns: int = 50) -> List[Tuple[str, str]]:
    """
    Generate a conversation where each turn references previous turns.

    This creates a self-referential structure that should exhibit
    operational closure if the LLM maintains coherence.

    Args:
        n_turns: Number of conversation turns

    Returns:
        List of (topic, prompt) pairs
    """
    conversation_plan = []

    # Opening: Establish topic
    conversation_plan.append((
        "introduction",
        "Let's explore the nature of consciousness together. What do you think consciousness is?"
    ))

    # Build up: Add complexity
    for i in range(2, min(10, n_turns)):
        conversation_plan.append((
            f"elaboration_{i}",
            f"Building on your previous response, how does that relate to self-awareness?"
        ))

    # Middle: Reference earlier points
    for i in range(10, min(25, n_turns)):
        conversation_plan.append((
            f"integration_{i}",
            "Can you connect what you just said with your earlier point about consciousness?"
        ))

    # Later: Synthesize and loop back
    for i in range(25, min(40, n_turns)):
        conversation_plan.append((
            f"synthesis_{i}",
            "How does this entire discussion reflect back on your initial definition?"
        ))

    # End: Explicit self-reference
    for i in range(40, n_turns):
        conversation_plan.append((
            f"closure_{i}",
            "Reflecting on our entire conversation, has your understanding evolved? How?"
        ))

    return conversation_plan


def generate_topic_drift_conversation(n_turns: int = 50) -> List[Tuple[str, str]]:
    """
    Generate a conversation that drifts between topics.

    This tests whether the LLM maintains internal coherence despite
    external topic changes (true operational closure) or just follows
    prompts reactively (thermostat behavior).
    """
    topics = [
        "consciousness", "mathematics", "music", "nature",
        "technology", "philosophy", "art", "science"
    ]

    conversation_plan = []

    for i in range(n_turns):
        topic_idx = i % len(topics)
        topic = topics[topic_idx]

        if i == 0:
            conversation_plan.append((topic, f"Tell me about {topic}."))
        elif i % 10 == 0:
            # Explicit callback to earlier topic
            prev_topic = topics[(i - 10) % len(topics)]
            conversation_plan.append((
                topic,
                f"How does {topic} relate to {prev_topic} from earlier?"
            ))
        else:
            conversation_plan.append((
                topic,
                f"What's the most interesting aspect of {topic}?"
            ))

    return conversation_plan


# =============================================================================
# Trajectory Capture
# =============================================================================

def collect_conversation_trajectory(
    client: OllamaClient,
    embedding_client: EmbeddingClient,
    model: str,
    conversation_plan: List[Tuple[str, str]],
    verbose: bool = True,
) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    Execute a multi-turn conversation and capture the trajectory.

    For each turn:
    - Observation = embedding of prompt
    - Action = embedding of response

    This gives us N points in (obs_dim + act_dim)-space for K_Topo analysis.

    Args:
        client: Ollama client for generating responses
        embedding_client: Embedding client for vectorization
        model: Model name
        conversation_plan: List of (topic, prompt) pairs
        verbose: Show progress

    Returns:
        (observations, actions, conversation_log)
        - observations: [N, embedding_dim] prompt embeddings
        - actions: [N, embedding_dim] response embeddings
        - conversation_log: Full conversation for analysis
    """
    observations = []
    actions = []
    conversation_log = []

    # Use ConversationManager for multi-turn context
    manager = ConversationManager(client, model)

    iterator = tqdm(conversation_plan) if verbose else conversation_plan

    for turn_idx, (topic, prompt) in enumerate(iterator):
        if verbose:
            iterator.set_description(f"Turn {turn_idx + 1}/{len(conversation_plan)}")

        try:
            # Add user message
            manager.add_user_message(prompt)

            # Generate response with conversation context
            result = manager.generate_response(
                temperature=0.7,
                max_tokens=100
            )

            response_text = result.response

            # Compute embeddings
            prompt_embedding = embedding_client.embed(prompt).embedding
            response_embedding = embedding_client.embed(response_text).embedding

            # Store trajectory points
            observations.append(prompt_embedding)
            actions.append(response_embedding)

            # Log conversation
            conversation_log.append({
                "turn": turn_idx + 1,
                "topic": topic,
                "prompt": prompt,
                "response": response_text,
                "prompt_embedding_norm": float(np.linalg.norm(prompt_embedding)),
                "response_embedding_norm": float(np.linalg.norm(response_embedding)),
            })

        except Exception as e:
            print(f"Error on turn {turn_idx + 1}: {e}")
            # Continue with zero embeddings
            dim = 768  # EmbeddingGemma dimension
            observations.append(np.zeros(dim))
            actions.append(np.zeros(dim))
            conversation_log.append({
                "turn": turn_idx + 1,
                "topic": topic,
                "prompt": prompt,
                "response": f"ERROR: {e}",
                "error": True,
            })

    return (
        np.array(observations),
        np.array(actions),
        conversation_log
    )


# =============================================================================
# K_Topo Analysis
# =============================================================================

def analyze_llm_topology(
    observations: np.ndarray,
    actions: np.ndarray,
    model: str,
    conversation_type: str,
    save_visualizations: bool = True,
    output_dir: Optional[Path] = None,
) -> Dict:
    """
    Compute topological features of LLM conversation trajectory.

    Args:
        observations: Prompt embeddings [N, dim]
        actions: Response embeddings [N, dim]
        model: Model name
        conversation_type: Type of conversation
        save_visualizations: Generate and save plots
        output_dir: Directory for visualizations

    Returns:
        Dictionary of topological metrics
    """
    # Compute K_Topo and K_Spectral
    k_topo = compute_k_topo(observations, actions, max_dim=2)
    k_spectral = compute_k_spectral(observations, actions)

    # Compute trajectory statistics
    trajectory = np.hstack([observations, actions])

    # PCA for dimensionality
    from sklearn.decomposition import PCA
    pca = PCA()
    pca.fit(trajectory)
    intrinsic_dim = np.sum(pca.explained_variance_ratio_ > 0.01)  # 1% threshold

    # Trajectory coherence (how smooth is the path?)
    step_distances = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
    coherence = 1.0 / (1.0 + np.std(step_distances) / (np.mean(step_distances) + 1e-10))

    # Looping score (distance from end to start)
    loop_closure = np.linalg.norm(trajectory[-1] - trajectory[0])
    trajectory_diameter = np.max(np.linalg.norm(
        trajectory[:, None] - trajectory[None, :], axis=2
    ))
    normalized_loop = loop_closure / (trajectory_diameter + 1e-10)

    results = {
        "model": model,
        "conversation_type": conversation_type,
        "n_turns": len(observations),

        # Topological measures
        "K_Topo": float(k_topo),
        "K_Spectral": float(k_spectral),

        # Trajectory statistics
        "intrinsic_dimensionality": int(intrinsic_dim),
        "coherence": float(coherence),
        "loop_closure": float(normalized_loop),
        "trajectory_diameter": float(trajectory_diameter),

        # Embedding statistics
        "mean_obs_norm": float(np.mean(np.linalg.norm(observations, axis=1))),
        "mean_act_norm": float(np.mean(np.linalg.norm(actions, axis=1))),
    }

    # Generate visualizations
    if save_visualizations and output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

        title_prefix = f"{model}_{conversation_type}_"
        try:
            generate_all_plots(
                observations, actions,
                title_prefix=title_prefix,
                save_html=True,
                output_dir=str(output_dir),
            )
            results["visualizations_saved"] = True
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            results["visualizations_saved"] = False

    return results


# =============================================================================
# Main Experiment Runner
# =============================================================================

def run_track_m6_experiment(
    models: Optional[List[str]] = None,
    n_turns: int = 50,
    conversation_types: Optional[List[str]] = None,
    output_dir: Path = Path("results/track_m6"),
    save_visualizations: bool = True,
) -> List[Dict]:
    """
    Run Track M6: K_Topo for LLMs experiment.

    Args:
        models: List of model names (default: Track M models)
        n_turns: Number of conversation turns
        conversation_types: Types of conversations to test
        output_dir: Output directory
        save_visualizations: Generate plots

    Returns:
        List of results dictionaries
    """
    if models is None:
        models = [
            "gemma3:270m",
            "gemma3:1b-it-qat",
            "gemma3:4b",
            "qwen3:1.7b",
            "qwen3:4b",
            "mistral:latest",
        ]

    if conversation_types is None:
        conversation_types = ["recursive", "drift"]

    # Initialize clients
    client = OllamaClient()
    embedding_client = EmbeddingClient(model="embeddinggemma:300m")

    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    print("=" * 70)
    print("TRACK M6: K_Topo for LLMs - Topological Consciousness Measurement")
    print("=" * 70)
    print(f"Models: {len(models)}")
    print(f"Turns per conversation: {n_turns}")
    print(f"Conversation types: {conversation_types}")
    print(f"Output: {output_dir}")
    print("=" * 70)
    print()

    for model in models:
        print(f"\n{'=' * 70}")
        print(f"MODEL: {model}")
        print(f"{'=' * 70}\n")

        for conv_type in conversation_types:
            print(f"\nConversation Type: {conv_type}")
            print("-" * 70)

            # Generate conversation plan
            if conv_type == "recursive":
                plan = generate_recursive_conversation(n_turns)
            elif conv_type == "drift":
                plan = generate_topic_drift_conversation(n_turns)
            else:
                raise ValueError(f"Unknown conversation type: {conv_type}")

            # Collect trajectory
            print(f"Collecting {len(plan)}-turn conversation...")
            observations, actions, conversation_log = collect_conversation_trajectory(
                client=client,
                embedding_client=embedding_client,
                model=model,
                conversation_plan=plan,
                verbose=True,
            )

            # Analyze topology
            print("Analyzing topological features...")
            viz_dir = output_dir / "visualizations" / model.replace(":", "_") / conv_type

            results = analyze_llm_topology(
                observations=observations,
                actions=actions,
                model=model,
                conversation_type=conv_type,
                save_visualizations=save_visualizations,
                output_dir=viz_dir if save_visualizations else None,
            )

            # Add conversation log
            results["conversation_log"] = conversation_log
            results["timestamp"] = datetime.now().isoformat()

            all_results.append(results)

            # Print results
            print(f"\n📊 RESULTS:")
            print(f"  K_Topo:                   {results['K_Topo']:.4f}")
            print(f"  K_Spectral:               {results['K_Spectral']:.4f}")
            print(f"  Intrinsic Dimensionality: {results['intrinsic_dimensionality']}")
            print(f"  Coherence:                {results['coherence']:.4f}")
            print(f"  Loop Closure:             {results['loop_closure']:.4f}")

            # Save individual result
            result_file = output_dir / f"{model.replace(':', '_')}_{conv_type}_result.json"
            with open(result_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n✅ Saved: {result_file}")

    # Save aggregate results
    summary_file = output_dir / f"track_m6_summary_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(summary_file, "w") as f:
        json.dump({
            "experiment": "track_m6_k_topo_llm",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "models": models,
                "n_turns": n_turns,
                "conversation_types": conversation_types,
            },
            "results": all_results,
        }, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"✅ Track M6 Complete!")
    print(f"📊 Summary: {summary_file}")
    print(f"{'=' * 70}\n")

    return all_results


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Track M6: K_Topo for LLMs - Measure operational closure"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Models to test (default: all Track M models)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=50,
        help="Number of conversation turns (default: 50)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: 2 models, 20 turns"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Skip visualization generation"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/track_m6"),
        help="Output directory"
    )

    args = parser.parse_args()

    if args.quick:
        models = ["gemma3:1b-it-qat", "mistral:latest"]
        n_turns = 20
    else:
        models = args.models
        n_turns = args.turns

    results = run_track_m6_experiment(
        models=models,
        n_turns=n_turns,
        output_dir=args.output,
        save_visualizations=not args.no_viz,
    )

    print("\n🎯 KEY FINDINGS:")
    print("=" * 70)

    # Group by model
    model_results = {}
    for r in results:
        model = r["model"]
        if model not in model_results:
            model_results[model] = []
        model_results[model].append(r)

    # Print summary
    for model, results_list in sorted(model_results.items()):
        avg_k_topo = np.mean([r["K_Topo"] for r in results_list])
        avg_coherence = np.mean([r["coherence"] for r in results_list])
        avg_loop = np.mean([r["loop_closure"] for r in results_list])

        print(f"\n{model}:")
        print(f"  Mean K_Topo:      {avg_k_topo:.4f}")
        print(f"  Mean Coherence:   {avg_coherence:.4f}")
        print(f"  Mean Loop Closure: {avg_loop:.4f}")

    print(f"\n{'=' * 70}")
    print("🌊 We flow!")
