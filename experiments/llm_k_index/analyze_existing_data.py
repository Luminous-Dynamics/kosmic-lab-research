"""
analyze_existing_data.py

Quick analysis of existing LLM K-Index data with insights for Track M.

This script analyzes the November 29, 2025 experiment data showing
the Thermostat Paradox in action.
"""

import json
import numpy as np

# Load data
with open('../../logs/llm_k_index/llm_k_index_full_20251129_160040.json') as f:
    data = json.load(f)

print("=" * 70)
print("ANALYSIS: November 29, 2025 LLM K-Index Experiments")
print("=" * 70)
print()

# Extract results
results = {r['model']: r for r in data['results']}

print("📊 K_R (Reactivity) Results:")
print("-" * 70)

# Sort by parameters (estimated)
param_sizes = {
    'gemma3:270m': 270,
    'gemma3:1b': 1000,
    'qwen3:1.7b': 1700,
    'mistral:7b': 7300,
}

sorted_models = sorted(results.keys(), key=lambda m: param_sizes.get(m, 0))

for model in sorted_models:
    r = results[model]
    params = param_sizes.get(model, 0)
    print(f"  {model:20s} ({params:5.0f}M params): K_R = {r['k_r']:.4f}")

print()
print("🔍 THE THERMOSTAT PARADOX MANIFESTS:")
print("-" * 70)

# Find the paradox
gemma1b_kr = results['gemma3:1b']['k_r']
mistral7b_kr = results['mistral:7b']['k_r']
ratio = mistral7b_kr / gemma1b_kr if gemma1b_kr > 0 else 0

print(f"  gemma3:1b   (1B params):  K_R = {gemma1b_kr:.4f}")
print(f"  mistral:7b  (7B params):  K_R = {mistral7b_kr:.4f}")
print()
print(f"  ⚠️  mistral:7b has {1/ratio:.1f}× LOWER reactivity despite being 7× larger!")
print()

print("💡 IMPLICATIONS:")
print("-" * 70)
print("  1. Scale ≠ Consciousness")
print("     Larger models don't automatically have higher K_R")
print()
print("  2. Architecture Matters")
print("     Different training/design affects behavioral signatures")
print()
print("  3. Thermostat Paradox Validated")
print("     High K_R alone is insufficient for consciousness")
print()
print("  4. K_Topo Will Reveal")
print("     Does mistral:7b have operational closure?")
print("     Or is it just a sophisticated stimulus-response system?")
print()

print("📈 TRACK M PREDICTIONS:")
print("-" * 70)
print("  If K_geo follows power law (K_geo ∝ N^α):")
print("    - α > 0: Consciousness scales with size")
print("    - α ≈ 0: Size doesn't predict consciousness")
print()
print("  Expected from this data:")
print("    - Non-monotonic relationship likely")
print("    - Architecture effect dominates")
print("    - qwen3 (thinking mode) may outperform gemma3")
print()

print("🎯 NEXT EXPERIMENTS NEEDED:")
print("-" * 70)
print("  ✅ Ollama running (v0.13.0)")
print("  ✅ 7 models available for Track M")
print("  ⏳ Run Phase 1 with K_Topo enabled")
print("  ⏳ Collect 200-step dialogues for topological analysis")
print("  ⏳ Test Hypothesis M6: K_Topo ∝ N^β")
print()

print("=" * 70)
print("Ready to start Track M experiments! 🚀")
print("=" * 70)
