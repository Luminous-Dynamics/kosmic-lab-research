"""
Ollama API Client for K-Index LLM Experiments.

Provides a clean interface for:
- Text generation with various models
- Conversation management
- Response timing and metadata collection
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

# Approved models from CLAUDE.md
APPROVED_MODELS = [
    "gemma3:270m",
    "gemma3:1b",
    "gemma3:1b-it-qat",
    "gemma3:4b",
    "gemma3n:e2b",
    "gemma3n:e4b",
    "qwen3:1.7b",
    "qwen3:4b",
    "mistral:7b",
    "embeddinggemma:300m",
]

# Default experiment models (subset for efficiency)
DEFAULT_EXPERIMENT_MODELS = [
    "gemma3:270m",   # Tiny baseline
    "gemma3:1b",     # Small
    "qwen3:1.7b",    # Hybrid thinking mode
    "mistral:7b",    # Capable baseline
]


@dataclass
class GenerationResult:
    """Result of a single generation call."""

    model: str
    prompt: str
    response: str
    prompt_tokens: int
    response_tokens: int
    total_duration_ms: float
    eval_duration_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    role: str  # "user" or "assistant"
    content: str
    tokens: int = 0
    timestamp: float = 0.0


class OllamaClient:
    """
    Client for Ollama API with K-Index experiment support.

    Example:
        >>> client = OllamaClient()
        >>> result = client.generate("gemma3:1b", "What is consciousness?")
        >>> print(result.response)
        >>> print(f"Generated in {result.total_duration_ms:.2f}ms")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify Ollama is running and accessible."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Ensure Ollama is running: {e}"
            )

    def list_models(self) -> List[str]:
        """List available models."""
        response = requests.get(
            f"{self.base_url}/api/tags",
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        return [m["name"] for m in data.get("models", [])]

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> GenerationResult:
        """
        Generate text from a prompt.

        Args:
            model: Model name (must be in APPROVED_MODELS)
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature (0 = deterministic)
            max_tokens: Maximum response tokens
            stream: Whether to stream the response

        Returns:
            GenerationResult with response and metadata

        Raises:
            ValueError: If model not approved
        """
        if model not in APPROVED_MODELS:
            raise ValueError(
                f"Model {model} not in approved list. "
                f"Approved: {APPROVED_MODELS}"
            )

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system:
            payload["system"] = system

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        total_duration = (time.time() - start_time) * 1000

        return GenerationResult(
            model=model,
            prompt=prompt,
            response=data.get("response", ""),
            prompt_tokens=data.get("prompt_eval_count", 0),
            response_tokens=data.get("eval_count", 0),
            total_duration_ms=total_duration,
            eval_duration_ms=data.get("eval_duration", 0) / 1e6,
            metadata={
                "context": data.get("context"),
                "done_reason": data.get("done_reason"),
            },
        )

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        """
        Chat completion with conversation history.

        Args:
            model: Model name
            messages: List of {"role": "user"|"assistant", "content": "..."}
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            GenerationResult with assistant's response
        """
        if model not in APPROVED_MODELS:
            raise ValueError(f"Model {model} not in approved list.")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        total_duration = (time.time() - start_time) * 1000

        assistant_response = data.get("message", {}).get("content", "")

        # Reconstruct prompt from messages for logging
        prompt_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )

        return GenerationResult(
            model=model,
            prompt=prompt_text,
            response=assistant_response,
            prompt_tokens=data.get("prompt_eval_count", 0),
            response_tokens=data.get("eval_count", 0),
            total_duration_ms=total_duration,
            eval_duration_ms=data.get("eval_duration", 0) / 1e6,
            metadata={
                "done_reason": data.get("done_reason"),
            },
        )


class ConversationManager:
    """
    Manages multi-turn conversations for K-Index experiments.

    Example:
        >>> manager = ConversationManager(client, "gemma3:1b")
        >>> manager.add_user_message("Tell me about consciousness.")
        >>> response = manager.generate_response()
        >>> print(response.response)
        >>> # Continue the conversation
        >>> manager.add_user_message("Can you elaborate?")
        >>> response2 = manager.generate_response()
    """

    def __init__(
        self,
        client: OllamaClient,
        model: str,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize conversation manager.

        Args:
            client: OllamaClient instance
            model: Model to use for this conversation
            system_prompt: Optional system prompt
        """
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.history: List[ConversationTurn] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self.history.append(ConversationTurn(
            role="user",
            content=content,
            timestamp=time.time(),
        ))

    def generate_response(
        self,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        """
        Generate assistant response based on conversation history.

        Returns:
            GenerationResult with response
        """
        messages = []

        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt,
            })

        for turn in self.history:
            messages.append({
                "role": turn.role,
                "content": turn.content,
            })

        result = self.client.chat(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Add assistant response to history
        self.history.append(ConversationTurn(
            role="assistant",
            content=result.response,
            tokens=result.response_tokens,
            timestamp=time.time(),
        ))

        return result

    def get_trajectory(self) -> List[Dict[str, Any]]:
        """
        Get the full conversation trajectory for K-Index analysis.

        Returns:
            List of turn dictionaries with role, content, tokens, timestamp
        """
        return [
            {
                "role": turn.role,
                "content": turn.content,
                "tokens": turn.tokens,
                "timestamp": turn.timestamp,
            }
            for turn in self.history
        ]

    def reset(self) -> None:
        """Clear conversation history."""
        self.history = []


def verify_models_available(
    models: Optional[List[str]] = None,
    client: Optional[OllamaClient] = None,
) -> Dict[str, bool]:
    """
    Check which models are available locally.

    Args:
        models: List of models to check (default: DEFAULT_EXPERIMENT_MODELS)
        client: OllamaClient instance (creates new if None)

    Returns:
        Dict mapping model name to availability
    """
    if client is None:
        client = OllamaClient()

    if models is None:
        models = DEFAULT_EXPERIMENT_MODELS

    available = client.list_models()
    return {model: model in available for model in models}


if __name__ == "__main__":
    # Quick test
    print("Testing Ollama client...")

    try:
        client = OllamaClient()
        available = verify_models_available()

        print("\nModel availability:")
        for model, is_available in available.items():
            status = "✓" if is_available else "✗"
            print(f"  {status} {model}")

        # Test generation with first available model
        for model, is_available in available.items():
            if is_available:
                print(f"\nTesting generation with {model}...")
                result = client.generate(
                    model,
                    "In one sentence, what is the meaning of life?",
                    temperature=0.0,
                )
                print(f"  Response: {result.response[:100]}...")
                print(f"  Tokens: {result.prompt_tokens} → {result.response_tokens}")
                print(f"  Duration: {result.total_duration_ms:.2f}ms")
                break

        print("\n✓ Ollama client working correctly")

    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
