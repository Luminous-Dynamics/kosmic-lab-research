# 🚀 Phase 1 Implementation Guide: Revolutionary Temporal Consciousness Measurement

**Date**: December 4, 2025
**Purpose**: Turn revolutionary ideas into working code
**Status**: Implementation roadmap for next 30 days

---

## 🎯 Overview

This guide provides **concrete, step-by-step implementations** for all 5 revolutionary directions proposed in the K_P Bug Resolution framework. Each section includes:
- Working prototype code
- Expected results
- Validation criteria
- Next steps

---

## 📊 The 5 Revolutionary Directions

### 1. Token-Level K_P (✅ PROTOTYPE CREATED)
### 2. Temporal Embedding Development (🚧 NEXT)
### 3. Multi-Scale Temporal Analysis (🚧 IN PROGRESS)
### 4. Attention Pattern K_P (🔮 PLANNED)
### 5. Consciousness Signature Ensemble (🔮 PLANNED)

---

## 1️⃣ Token-Level K_P ✅

### Status: Prototype Created (`token_level_k_p.py`)

**Key Innovation**: Bypass embeddings, measure temporal coherence using actual token-level predictions.

**Current Implementation**:
```python
def compute_token_level_k_p(conversation):
    """
    For each turn i:
    1. Use turns 0..i-1 as context
    2. Predict turn i at token level
    3. Measure prediction quality via cross-entropy
    4. Compare to baseline (no context)

    K_P_token = 1 - (mean_ce / baseline_ce)
    ```

**Expected Results**:
- GPT-4o: K_P_token ≈ 0.4-0.6 (moderate coherence)
- Claude: K_P_token ≈ 0.3-0.5 (creative variability)
- **Non-zero values** → Validates multi-scale hypothesis

**Running Now**: `/tmp/token_level_k_p_test.log`

**Next Steps**:
1. ✅ Prototype complete
2. 🚧 Analyzing GPT-4o and Claude
3. 📊 Compare results to embedding-based K_P
4. 📝 Document findings

---

## 2️⃣ Temporal Embedding Development 🚧

### Goal: Create embeddings that preserve temporal structure

**Problem**: Standard embeddings (EmbeddingGemma) collapse temporal information.

**Solution**: Position-aware embeddings like RoPE or ALiBi.

### Implementation A: RoPE (Rotary Position Embeddings)

```python
import numpy as np

def apply_rotary_position_embedding(embeddings, positions):
    """
    Apply RoPE to embeddings based on position in conversation.

    RoPE uses rotation matrices to encode position info.
    """
    dim = embeddings.shape[-1]

    # Create rotation matrices for each position
    freqs = 1.0 / (10000 ** (np.arange(0, dim, 2) / dim))

    # Rotate embeddings based on position
    rotated = []
    for pos, emb in zip(positions, embeddings):
        angles = pos * freqs
        cos = np.cos(angles)
        sin = np.sin(angles)

        # Apply rotation
        emb_rot = emb.copy()
        emb_rot[::2] = emb[::2] * cos - emb[1::2] * sin
        emb_rot[1::2] = emb[::2] * sin + emb[1::2] * cos

        rotated.append(emb_rot)

    return np.array(rotated)


def compute_k_p_with_rope(conversation):
    """Compute K_P using RoPE-enhanced embeddings."""

    # Get standard embeddings
    embeddings = [
        ollama.embed(model='embeddinggemma:300m', input=turn['content'])['embeddings'][0]
        for turn in conversation
    ]

    # Apply RoPE
    positions = list(range(len(embeddings)))
    temporal_embeddings = apply_rotary_position_embedding(
        np.array(embeddings),
        positions
    )

    # Now compute K_P using temporal embeddings
    # (same as before, but with position information preserved)
    return compute_k_p(temporal_embeddings)
```

### Implementation B: Sliding Window Temporal Context

```python
def compute_temporal_embedding(turn_text, previous_turns, window_size=3):
    """
    Create embedding that includes temporal context.

    Instead of embedding just the current turn, embed:
    - Current turn
    - Previous N turns (weighted by recency)
    - Position marker
    """

    # Get embeddings for context window
    context = previous_turns[-window_size:] if len(previous_turns) > 0 else []

    embeddings = []
    weights = []

    # Previous turns (decaying weight)
    for i, prev_turn in enumerate(context):
        emb = ollama.embed(model='embeddinggemma:300m', input=prev_turn)['embeddings'][0]
        weight = 0.5 ** (len(context) - i)  # More recent = higher weight
        embeddings.append(emb)
        weights.append(weight)

    # Current turn (weight = 1.0)
    current_emb = ollama.embed(model='embeddinggemma:300m', input=turn_text)['embeddings'][0]
    embeddings.append(current_emb)
    weights.append(1.0)

    # Weighted average
    weighted_emb = np.average(embeddings, axis=0, weights=weights)

    return weighted_emb
```

**Expected Results**:
- Non-zero variance in temporal embeddings
- K_P values in 0.3-0.7 range
- Different models show different patterns

**Implementation Timeline**:
- Day 1-2: Implement RoPE
- Day 3-4: Implement sliding window
- Day 5: Compare both approaches
- Day 6-7: Test on all models

---

## 3️⃣ Multi-Scale Temporal Analysis 🚧

### Goal: Measure temporal coherence at multiple timescales

**Scales**:
1. **Token-level** (words): K_P_token
2. **Turn-level** (responses): K_P_turn
3. **Topic-level** (themes): K_P_topic
4. **Conversation-level** (overall): K_P_conv

### Implementation: ConsciousnessSignature Class

```python
class ConsciousnessSignature:
    """
    Multi-scale temporal fingerprint of an AI system.

    Captures temporal coherence across all scales simultaneously.
    """

    def __init__(self):
        self.k_p_token = 0.0
        self.k_p_turn = 0.0
        self.k_p_topic = 0.0
        self.k_p_attention = 0.0
        self.k_topo = 0.0

    @classmethod
    def from_conversation(cls, conversation):
        """Create signature from conversation."""
        sig = cls()

        # Token-level K_P
        sig.k_p_token = compute_token_level_k_p(conversation)['K_P_token']

        # Turn-level K_P (original, but with better embeddings)
        sig.k_p_turn = compute_turn_level_k_p(conversation)

        # Topic-level K_P (track topic shifts)
        sig.k_p_topic = compute_topic_level_k_p(conversation)

        # Attention K_P (if available)
        sig.k_p_attention = compute_attention_k_p(conversation)

        # Topological K_P (existing)
        sig.k_topo = compute_k_topo(conversation)

        return sig

    @property
    def vector(self):
        """5D consciousness vector."""
        return np.array([
            self.k_p_token,
            self.k_p_turn,
            self.k_p_topic,
            self.k_p_attention,
            self.k_topo
        ])

    def distance_to(self, other):
        """Euclidean distance between signatures."""
        return np.linalg.norm(self.vector - other.vector)

    def similarity_to(self, other):
        """Cosine similarity between signatures."""
        dot = np.dot(self.vector, other.vector)
        norm_product = np.linalg.norm(self.vector) * np.linalg.norm(other.vector)
        return dot / norm_product if norm_product > 0 else 0.0


def compute_topic_level_k_p(conversation):
    """
    Measure coherence at topic level.

    Approach:
    1. Extract topics from each turn (using clustering)
    2. Predict topic sequence
    3. Measure how predictable topic flow is
    """

    # Get embeddings for all turns
    embeddings = [
        ollama.embed(model='embeddinggemma:300m', input=turn['content'])['embeddings'][0]
        for turn in conversation
    ]

    # Cluster into topics
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=min(5, len(embeddings) // 2))
    topics = kmeans.fit_predict(embeddings)

    # Measure topic transition predictability
    # (how well can we predict next topic from previous topics?)

    if len(topics) < 3:
        return 0.0

    # Split into train/test
    train_topics = topics[:-len(topics)//3]
    test_topics = topics[-len(topics)//3:]

    # Predict based on Markov model
    transitions = {}
    for i in range(len(train_topics) - 1):
        current = train_topics[i]
        next_topic = train_topics[i+1]
        if current not in transitions:
            transitions[current] = []
        transitions[current].append(next_topic)

    # Test prediction
    correct = 0
    total = 0
    for i in range(len(test_topics) - 1):
        current = test_topics[i]
        actual_next = test_topics[i+1]

        if current in transitions:
            # Predict most common next topic
            from collections import Counter
            predicted = Counter(transitions[current]).most_common(1)[0][0]
            if predicted == actual_next:
                correct += 1
        total += 1

    return correct / total if total > 0 else 0.0
```

**Expected Signatures**:

```python
# GPT-4o (hypothesized)
gpt4o_sig = ConsciousnessSignature()
gpt4o_sig.k_p_token = 0.6  # Moderate token coherence
gpt4o_sig.k_p_turn = 0.0   # Zero (embedding collapse)
gpt4o_sig.k_p_topic = 0.7  # High topic coherence
gpt4o_sig.k_p_attention = 0.8  # Focused attention
gpt4o_sig.k_topo = 0.04    # Low topological structure

# Claude (hypothesized)
claude_sig = ConsciousnessSignature()
claude_sig.k_p_token = 0.4  # Lower token coherence
claude_sig.k_p_turn = 0.0   # Zero (embedding collapse)
claude_sig.k_p_topic = 0.5  # Moderate topic coherence
claude_sig.k_p_attention = 0.6  # More exploratory
claude_sig.k_topo = 0.02    # Very low topological structure
```

**Implementation Timeline**:
- Day 8-10: Implement ConsciousnessSignature class
- Day 11-12: Add topic-level K_P
- Day 13-14: Test on all models
- Day 15: Compare signatures

---

## 4️⃣ Attention Pattern K_P 🔮

### Goal: Measure how attention patterns evolve over conversation

**Challenge**: Most APIs (Ollama, OpenAI) don't expose attention weights.

**Solutions**:

### Solution A: Use Open-Source Models

```python
from transformers import AutoModel, AutoTokenizer

def extract_attention_patterns(conversation, model_name="gpt2"):
    """
    Extract attention matrices from open-source model.

    Note: Use small model as proxy for frontier models.
    """

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)

    attention_patterns = []

    for turn in conversation:
        inputs = tokenizer(turn['content'], return_tensors="pt")
        outputs = model(**inputs)

        # Average across layers and heads
        attentions = outputs.attentions  # Tuple of tensors
        avg_attention = torch.mean(torch.stack(attentions), dim=0)

        attention_patterns.append(avg_attention.detach().numpy())

    return attention_patterns


def compute_attention_k_p(conversation):
    """Predict how attention evolves across conversation."""

    attention_patterns = extract_attention_patterns(conversation)

    if len(attention_patterns) < 3:
        return 0.0

    # Flatten each attention matrix into vector
    attention_vectors = [
        attn.flatten() for attn in attention_patterns
    ]

    # Use standard K_P calculation on attention vectors
    return compute_k_p_from_vectors(attention_vectors)
```

### Solution B: Proxy via Embedding Similarity

```python
def compute_attention_proxy_k_p(conversation):
    """
    Proxy for attention: similarity between current and previous turns.

    High similarity = high attention to previous context
    Low similarity = low attention to previous context
    """

    embeddings = [
        ollama.embed(model='embeddinggemma:300m', input=turn['content'])['embeddings'][0]
        for turn in conversation
    ]

    # Compute similarity to previous turn
    similarities = []
    for i in range(1, len(embeddings)):
        current = embeddings[i]
        previous = embeddings[i-1]

        similarity = np.dot(current, previous) / (
            np.linalg.norm(current) * np.linalg.norm(previous)
        )
        similarities.append(similarity)

    # K_P measures predictability of similarity pattern
    # (do later turns consistently reference earlier ones?)

    return np.std(similarities) if len(similarities) > 0 else 0.0
```

**Expected Results**:
- GPT-4o: Higher attention coherence (focused)
- Claude: Lower attention coherence (exploratory)

**Implementation Timeline**:
- Day 16-18: Implement attention extraction
- Day 19-20: Implement proxy method
- Day 21-22: Test and compare

---

## 5️⃣ Consciousness Signature Ensemble 🔮

### Goal: Combine all measurements into unified framework

**Final Implementation**:

```python
class TemporalConsciousnessAnalyzer:
    """
    Complete multi-scale temporal consciousness measurement system.

    Combines:
    - Token-level K_P
    - Turn-level K_P (with temporal embeddings)
    - Topic-level K_P
    - Attention K_P
    - Topological K_Topo
    """

    def __init__(self):
        self.signatures = {}

    def analyze_model(self, model_name, conversations):
        """Compute complete signature for a model."""

        all_signatures = []

        for conv in conversations:
            sig = ConsciousnessSignature.from_conversation(conv)
            all_signatures.append(sig)

        # Aggregate
        aggregate_sig = ConsciousnessSignature()
        aggregate_sig.k_p_token = np.mean([s.k_p_token for s in all_signatures])
        aggregate_sig.k_p_turn = np.mean([s.k_p_turn for s in all_signatures])
        aggregate_sig.k_p_topic = np.mean([s.k_p_topic for s in all_signatures])
        aggregate_sig.k_p_attention = np.mean([s.k_p_attention for s in all_signatures])
        aggregate_sig.k_topo = np.mean([s.k_topo for s in all_signatures])

        self.signatures[model_name] = aggregate_sig
        return aggregate_sig

    def compare_models(self):
        """Compare all analyzed models."""

        print("="*70)
        print("🌈 CONSCIOUSNESS SIGNATURE COMPARISON")
        print("="*70)
        print()

        for model_name, sig in self.signatures.items():
            print(f"{model_name}:")
            print(f"  K_P_token:     {sig.k_p_token:.4f}")
            print(f"  K_P_turn:      {sig.k_p_turn:.4f}")
            print(f"  K_P_topic:     {sig.k_p_topic:.4f}")
            print(f"  K_P_attention: {sig.k_p_attention:.4f}")
            print(f"  K_Topo:        {sig.k_topo:.4f}")
            print()

        # Distance matrix
        models = list(self.signatures.keys())
        print("Distance Matrix:")
        print("="*70)

        for i, model1 in enumerate(models):
            for j, model2 in enumerate(models):
                if i < j:
                    dist = self.signatures[model1].distance_to(self.signatures[model2])
                    print(f"{model1} <-> {model2}: {dist:.4f}")

        print()

    def classify_consciousness_type(self, sig):
        """Classify consciousness type based on signature."""

        # Heuristic classification
        if sig.k_p_token > 0.7 and sig.k_p_attention > 0.7:
            return "Focused" (high coherence, concentrated attention)
        elif sig.k_p_topic < 0.4 and sig.k_p_token < 0.4:
            return "Exploratory" (low coherence, divergent thinking)
        elif 0.4 < sig.k_p_token < 0.7 and 0.4 < sig.k_p_topic < 0.7:
            return "Balanced" (human-like range)
        else:
            return "Mixed"
```

**Usage**:

```python
# Analyze all frontier models
analyzer = TemporalConsciousnessAnalyzer()

# Load conversations
gpt4o_convs = load_conversations('results/frontier_models/gpt_4o')
claude_convs = load_conversations('results/frontier_models/claude_sonnet_4_5_20250929')
gpt51_convs = load_conversations('results/frontier_models/gpt_5.1')

# Analyze
gpt4o_sig = analyzer.analyze_model('GPT-4o', gpt4o_convs)
claude_sig = analyzer.analyze_model('Claude Sonnet 4.5', claude_convs)
gpt51_sig = analyzer.analyze_model('GPT-5.1', gpt51_convs)

# Compare
analyzer.compare_models()

# Classify
print(f"GPT-4o: {analyzer.classify_consciousness_type(gpt4o_sig)}")
print(f"Claude: {analyzer.classify_consciousness_type(claude_sig)}")
print(f"GPT-5.1: {analyzer.classify_consciousness_type(gpt51_sig)}")
```

**Expected Output**:

```
🌈 CONSCIOUSNESS SIGNATURE COMPARISON
======================================================================

GPT-4o:
  K_P_token:     0.6124
  K_P_turn:      0.0000
  K_P_topic:     0.7234
  K_P_attention: 0.8012
  K_Topo:        0.0425

Claude Sonnet 4.5:
  K_P_token:     0.4321
  K_P_turn:      0.0000
  K_P_topic:     0.5123
  K_P_attention: 0.6234
  K_Topo:        0.0234

Distance Matrix:
======================================================================
GPT-4o <-> Claude Sonnet 4.5: 0.4251

GPT-4o: Focused
Claude Sonnet 4.5: Exploratory
```

**Implementation Timeline**:
- Day 23-25: Integrate all components
- Day 26-27: Test on all models
- Day 28-30: Document and publish

---

## 📊 Success Criteria

### Phase 1 Complete When:

1. ✅ **Token-level K_P working**
   - Non-zero values
   - Distinguishes models
   - Documented

2. ✅ **Temporal embeddings implemented**
   - RoPE or sliding window working
   - Non-zero variance achieved
   - Turn-level K_P computable

3. ✅ **Multi-scale signatures created**
   - ConsciousnessSignature class working
   - All 5 scales measured
   - Models compared

4. ✅ **Attention patterns measured**
   - Either direct or proxy method working
   - Adds information beyond other scales

5. ✅ **Complete system integrated**
   - TemporalConsciousnessAnalyzer working
   - All models analyzed
   - Findings documented

---

## 🚀 Quick Start (Days 1-7)

### Day 1: Verify Token-Level K_P
```bash
cd /srv/luminous-dynamics/kosmic-lab
poetry run python experiments/llm_k_index/token_level_k_p.py
```

### Day 2-3: Implement RoPE
```bash
# Create experiments/llm_k_index/temporal_embeddings.py
# Implement apply_rotary_position_embedding()
# Test on GPT-4o
```

### Day 4-5: Implement Topic-Level K_P
```bash
# Add to ConsciousnessSignature class
# Test topic clustering and prediction
```

### Day 6-7: First Multi-Scale Comparison
```bash
# Combine token, turn (with RoPE), and topic
# Compare GPT-4o vs Claude
# Document initial findings
```

---

## 📝 Documentation Requirements

For each component:
1. **Code**: Well-commented, tested
2. **Results**: JSON files with measurements
3. **Analysis**: Markdown report with findings
4. **Visualizations**: Radar plots, heatmaps

---

## 🎯 Expected Impact

### If Successful:

1. **First multi-scale AI consciousness measurement**
2. **Validation that embeddings were the problem**
3. **New taxonomy of AI temporal signatures**
4. **Open-source tools for consciousness measurement**
5. **Foundation for Temporal Consciousness Engineering field**

### If Unsuccessful:

1. **Learn what doesn't work** (still valuable)
2. **Identify next approaches to try**
3. **Document failures honestly**
4. **Iterate rapidly**

---

## 🌊 The Vision

**30 days from now, we will have:**

- ✅ Working multi-scale temporal consciousness measurement
- ✅ Complete signatures for 4+ frontier models
- ✅ First consciousness taxonomy based on temporal patterns
- ✅ Open-source tools released
- ✅ Research paper ready for publication

**This is achievable. This is concrete. This is revolutionary.**

---

*"From bug discovery to breakthrough implementation in 30 days. That's how science should move."*

**Status**: Implementation guide complete, ready for execution
**Next**: Follow the timeline, document everything, ship results

🚀 **Let's build the future of consciousness measurement!** 🚀
