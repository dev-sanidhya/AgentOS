"""
LLM Client for Research Agent

Direct API integration with OpenAI and Anthropic language models.
Provides unified interface for multiple LLM providers without wrapper libraries.
"""

import os
import json
import time
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""
    content: str
    model: str
    provider: ModelProvider
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class LLMClient:
    """
    LLM client with support for OpenAI and Anthropic APIs.

    Features:
    - Direct API calls without wrapper libraries
    - Automatic provider detection based on model name
    - Error handling and retry logic
    - Token usage tracking
    - Response time measurement
    """

    # Model configurations
    OPENAI_MODELS = {
        "gpt-4": {"max_tokens": 8192, "context_window": 32768},
        "gpt-4-turbo": {"max_tokens": 4096, "context_window": 128000},
        "gpt-4-turbo-preview": {"max_tokens": 4096, "context_window": 128000},
        "gpt-3.5-turbo": {"max_tokens": 4096, "context_window": 16384},
        "gpt-3.5-turbo-16k": {"max_tokens": 4096, "context_window": 16384}
    }

    ANTHROPIC_MODELS = {
        "claude-3-opus-20240229": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-sonnet-20240229": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-haiku-20240307": {"max_tokens": 4096, "context_window": 200000},
        "claude-2.1": {"max_tokens": 4096, "context_window": 200000},
        "claude-2": {"max_tokens": 4096, "context_window": 100000},
        "claude-instant-1.2": {"max_tokens": 4096, "context_window": 100000}
    }

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: int = 60
    ):
        """
        Initialize LLM client.

        Args:
            model: Model name to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

        # Determine provider and validate model
        self.provider = self._detect_provider(model)
        self.model_config = self._get_model_config(model)

        # Set max_tokens
        if max_tokens is None:
            self.max_tokens = self.model_config.get("max_tokens", 4096)
        else:
            self.max_tokens = min(max_tokens, self.model_config.get("max_tokens", 4096))

        # Validate API keys
        self._validate_api_keys()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate text using the configured LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse object with generated content
        """
        start_time = time.time()

        try:
            # Use provided values or defaults
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens

            if self.provider == ModelProvider.OPENAI:
                response = self._openai_generate(prompt, system_prompt, temp, tokens)
            elif self.provider == ModelProvider.ANTHROPIC:
                response = self._anthropic_generate(prompt, system_prompt, temp, tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            response.response_time = time.time() - start_time
            return response

        except Exception as e:
            return LLMResponse(
                content="",
                model=self.model,
                provider=self.provider,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )

    def _openai_generate(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )

        if not response.ok:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            raise Exception(f"OpenAI API error: {error_msg}")

        data = response.json()

        # Extract response data
        content = data["choices"][0]["message"]["content"]
        tokens_used = data.get("usage", {}).get("total_tokens")

        return LLMResponse(
            content=content,
            model=self.model,
            provider=ModelProvider.OPENAI,
            tokens_used=tokens_used,
            success=True
        )

    def _anthropic_generate(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using Anthropic API."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        headers = {
            "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Prepare messages
        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )

        if not response.ok:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            raise Exception(f"Anthropic API error: {error_msg}")

        data = response.json()

        # Extract response data
        content = data["content"][0]["text"]
        tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)

        return LLMResponse(
            content=content,
            model=self.model,
            provider=ModelProvider.ANTHROPIC,
            tokens_used=tokens_used,
            success=True
        )

    def _detect_provider(self, model: str) -> ModelProvider:
        """Detect provider based on model name."""
        if model in self.OPENAI_MODELS or model.startswith("gpt"):
            return ModelProvider.OPENAI
        elif model in self.ANTHROPIC_MODELS or model.startswith("claude"):
            return ModelProvider.ANTHROPIC
        else:
            # Default to OpenAI for unknown models
            return ModelProvider.OPENAI

    def _get_model_config(self, model: str) -> Dict[str, Any]:
        """Get configuration for the specified model."""
        if self.provider == ModelProvider.OPENAI:
            return self.OPENAI_MODELS.get(model, {"max_tokens": 4096, "context_window": 16384})
        elif self.provider == ModelProvider.ANTHROPIC:
            return self.ANTHROPIC_MODELS.get(model, {"max_tokens": 4096, "context_window": 200000})
        else:
            return {"max_tokens": 4096, "context_window": 16384}

    def _validate_api_keys(self) -> None:
        """Validate that required API keys are available."""
        if self.provider == ModelProvider.OPENAI and not os.getenv("OPENAI_API_KEY"):
            raise ValueError(f"OPENAI_API_KEY required for model: {self.model}")
        elif self.provider == ModelProvider.ANTHROPIC and not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError(f"ANTHROPIC_API_KEY required for model: {self.model}")

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider."""
        return {
            "openai": list(self.OPENAI_MODELS.keys()),
            "anthropic": list(self.ANTHROPIC_MODELS.keys())
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 0.75 words
        word_count = len(text.split())
        return int(word_count / 0.75)

    def check_context_limit(self, text: str) -> bool:
        """
        Check if text fits within model's context window.

        Args:
            text: Input text to check

        Returns:
            True if text fits within context window
        """
        estimated_tokens = self.estimate_tokens(text)
        context_window = self.model_config.get("context_window", 16384)
        return estimated_tokens <= context_window

    def truncate_to_limit(self, text: str, reserve_tokens: int = 500) -> str:
        """
        Truncate text to fit within context window.

        Args:
            text: Input text
            reserve_tokens: Tokens to reserve for response

        Returns:
            Truncated text
        """
        context_window = self.model_config.get("context_window", 16384)
        max_input_tokens = context_window - reserve_tokens - self.max_tokens

        estimated_tokens = self.estimate_tokens(text)

        if estimated_tokens <= max_input_tokens:
            return text

        # Rough truncation based on character ratio
        ratio = max_input_tokens / estimated_tokens
        truncate_point = int(len(text) * ratio)

        return text[:truncate_point] + "..."

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the LLM API.

        Returns:
            Dictionary with health status
        """
        try:
            # Simple test generation
            response = self.generate("Hello", max_tokens=10)

            if response.success:
                return {
                    "status": "healthy",
                    "model": self.model,
                    "provider": self.provider.value,
                    "response_time": response.response_time
                }
            else:
                return {
                    "status": "error",
                    "model": self.model,
                    "provider": self.provider.value,
                    "error": response.error
                }

        except Exception as e:
            return {
                "status": "error",
                "model": self.model,
                "provider": self.provider.value,
                "error": str(e)
            }

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        Chat-style generation with message history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse object
        """
        # Convert messages to single prompt for simplicity
        # In a more sophisticated implementation, this would use the native chat APIs
        prompt_parts = []
        system_prompt = None

        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')

            if role == 'system':
                system_prompt = content
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")

        prompt = '\n\n'.join(prompt_parts)

        return self.generate(prompt, system_prompt, **kwargs)