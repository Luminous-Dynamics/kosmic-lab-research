"""
Embedding Client for K-Index LLM Experiments.

Converts text to numerical vectors for K-Index computation.
Uses Ollama's embedding API with embeddinggemma:300m.
"""

import hashlib
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests

EMBEDDING_MODEL = "embeddinggemma:300m"
EMBEDDING_DIM = 768  # EmbeddingGemma output dimension


@dataclass
class EmbeddingResult:
    """Result of an embedding computation."""

    text: str
    embedding: np.ndarray
    norm: float
    model: str


class EmbeddingClient:
    """
    Client for computing text embeddings via Ollama.

    Uses embeddinggemma:300m for high-quality sentence embeddings.

    Example:
        >>> client = EmbeddingClient()
        >>> result = client.embed("What is consciousness?")
        >>> print(f"Embedding norm: {result.norm:.4f}")
        >>> print(f"Embedding dim: {result.embedding.shape}")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = EMBEDDING_MODEL,
        cache_size: int = 1000,
    ):
        """
        Initialize embedding client.

        Args:
            base_url: Ollama API base URL
            model: Embedding model to use
            cache_size: LRU cache size for embeddings
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._cache: Dict[str, np.ndarray] = {}
        self._cache_size = cache_size
        self._verify_model()

    def _verify_model(self) -> None:
        """Verify embedding model is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            if self.model not in models:
                raise ValueError(
                    f"Embedding model {self.model} not available. "
                    f"Run: ollama pull {self.model}"
                )
        except requests.RequestException as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}")

    def _text_hash(self, text: str) -> str:
        """Compute hash for cache key."""
        return hashlib.md5(text.encode()).hexdigest()

    def embed(self, text: str, use_cache: bool = True) -> EmbeddingResult:
        """
        Compute embedding for text.

        Args:
            text: Input text to embed
            use_cache: Whether to use LRU cache

        Returns:
            EmbeddingResult with embedding vector and metadata
        """
        cache_key = self._text_hash(text)

        if use_cache and cache_key in self._cache:
            embedding = self._cache[cache_key]
            return EmbeddingResult(
                text=text,
                embedding=embedding,
                norm=float(np.linalg.norm(embedding)),
                model=self.model,
            )

        response = requests.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": text},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        # Handle both single and batch embeddings
        embeddings = data.get("embeddings", [])
        if embeddings:
            embedding = np.array(embeddings[0], dtype=np.float32)
        else:
            # Fallback for older API format
            embedding = np.array(data.get("embedding", []), dtype=np.float32)

        # Cache management
        if use_cache:
            if len(self._cache) >= self._cache_size:
                # Remove oldest entry (simple FIFO, not true LRU)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[cache_key] = embedding

        return EmbeddingResult(
            text=text,
            embedding=embedding,
            norm=float(np.linalg.norm(embedding)),
            model=self.model,
        )

    def embed_batch(
        self,
        texts: List[str],
        use_cache: bool = True,
    ) -> List[EmbeddingResult]:
        """
        Compute embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            use_cache: Whether to use LRU cache

        Returns:
            List of EmbeddingResults
        """
        return [self.embed(text, use_cache=use_cache) for text in texts]

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        metric: str = "cosine",
    ) -> float:
        """
        Compute similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            metric: Similarity metric ("cosine" or "euclidean")

        Returns:
            Similarity score
        """
        emb1 = self.embed(text1).embedding
        emb2 = self.embed(text2).embedding

        if metric == "cosine":
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            if norm1 < 1e-10 or norm2 < 1e-10:
                return 0.0
            return float(np.dot(emb1, emb2) / (norm1 * norm2))
        elif metric == "euclidean":
            return float(-np.linalg.norm(emb1 - emb2))  # Negative for similarity
        else:
            raise ValueError(f"Unknown metric: {metric}")


def compute_text_norms(
    texts: List[str],
    client: Optional[EmbeddingClient] = None,
) -> np.ndarray:
    """
    Compute L2 norms of text embeddings.

    This is the core operation for K-Index:
    ||O|| = norm of observation embedding
    ||A|| = norm of action (response) embedding

    Args:
        texts: List of texts
        client: EmbeddingClient (creates new if None)

    Returns:
        Array of L2 norms
    """
    if client is None:
        client = EmbeddingClient()

    results = client.embed_batch(texts)
    return np.array([r.norm for r in results], dtype=np.float32)


def compute_embedding_entropy(
    texts: List[str],
    client: Optional[EmbeddingClient] = None,
    n_bins: int = 32,
) -> float:
    """
    Compute Shannon entropy of embedding norm distribution.

    Used for K_I (integration) computation.

    Args:
        texts: List of texts
        client: EmbeddingClient
        n_bins: Number of histogram bins

    Returns:
        Shannon entropy in nats
    """
    norms = compute_text_norms(texts, client)

    if len(norms) < 2:
        return 0.0

    hist, _ = np.histogram(norms, bins=n_bins, density=True)
    p = hist / (np.sum(hist) + 1e-12)
    p = p[p > 0]

    return float(-np.sum(p * np.log(p))) if len(p) > 0 else 0.0


def compute_embedding_correlation(
    texts1: List[str],
    texts2: List[str],
    client: Optional[EmbeddingClient] = None,
) -> Tuple[float, float]:
    """
    Compute Pearson correlation between embedding norms of two text sets.

    Core operation for K_R (reactivity) and K_S (social).

    Args:
        texts1: First text set (e.g., prompts)
        texts2: Second text set (e.g., responses)
        client: EmbeddingClient

    Returns:
        Tuple of (correlation, p-value)
    """
    if client is None:
        client = EmbeddingClient()

    norms1 = compute_text_norms(texts1, client)
    norms2 = compute_text_norms(texts2, client)

    min_len = min(len(norms1), len(norms2))
    norms1 = norms1[:min_len]
    norms2 = norms2[:min_len]

    if np.std(norms1) < 1e-10 or np.std(norms2) < 1e-10:
        return 0.0, 1.0

    correlation = np.corrcoef(norms1, norms2)[0, 1]
    if np.isnan(correlation):
        return 0.0, 1.0

    # Compute p-value (t-test for correlation)
    n = len(norms1)
    if n > 2 and abs(correlation) < 1.0:
        t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2))
        # Two-tailed p-value approximation
        from scipy import stats
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
    else:
        p_value = 1.0

    return float(correlation), float(p_value)


class TextFeatureExtractor:
    """
    Extract features from text for K-Index computation.

    Computes:
    - Embedding norm (||x||)
    - Token count
    - Information density (compression ratio)
    - Vocabulary diversity
    """

    def __init__(self, embedding_client: Optional[EmbeddingClient] = None):
        """Initialize with optional embedding client."""
        self.embedding_client = embedding_client or EmbeddingClient()

    def extract_features(self, text: str) -> Dict[str, float]:
        """
        Extract all features from text.

        Returns:
            Dictionary of feature name to value
        """
        import gzip

        # Embedding features
        emb_result = self.embedding_client.embed(text)

        # Token count (simple whitespace approximation)
        tokens = text.split()
        token_count = len(tokens)

        # Information density (compression ratio)
        text_bytes = text.encode("utf-8")
        compressed = gzip.compress(text_bytes)
        info_density = len(compressed) / max(len(text_bytes), 1)

        # Vocabulary diversity (unique tokens / total tokens)
        vocab_diversity = len(set(tokens)) / max(token_count, 1)

        # Character diversity
        char_diversity = len(set(text)) / max(len(text), 1)

        return {
            "embedding_norm": emb_result.norm,
            "token_count": float(token_count),
            "char_count": float(len(text)),
            "info_density": info_density,
            "vocab_diversity": vocab_diversity,
            "char_diversity": char_diversity,
        }

    def extract_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Extract features from multiple texts."""
        return [self.extract_features(text) for text in texts]


if __name__ == "__main__":
    # Quick test
    print("Testing embedding client...")

    try:
        client = EmbeddingClient()

        test_texts = [
            "What is consciousness?",
            "The weather is nice today.",
            "Quantum mechanics describes the behavior of particles at the smallest scales.",
        ]

        print("\nEmbedding texts:")
        for text in test_texts:
            result = client.embed(text)
            print(f"  '{text[:40]}...'")
            print(f"    Norm: {result.norm:.4f}")
            print(f"    Dim: {result.embedding.shape}")

        print("\nSimilarity matrix:")
        for i, t1 in enumerate(test_texts):
            for j, t2 in enumerate(test_texts):
                sim = client.compute_similarity(t1, t2)
                print(f"  [{i},{j}]: {sim:.4f}")

        print("\nFeature extraction:")
        extractor = TextFeatureExtractor(client)
        features = extractor.extract_features(test_texts[2])
        for k, v in features.items():
            print(f"  {k}: {v:.4f}")

        print("\n✓ Embedding client working correctly")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
