"""
LLM Client for Code Review Agent

This module provides direct API access to various LLM providers (OpenAI, Anthropic)
without using wrapper libraries. It handles authentication, rate limiting, error handling,
and response parsing for code review operations.
"""

import os
import time
import json
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class LLMResponse:
    """Response from an LLM API call."""
    content: str
    model: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    response_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    model: str
    temperature: float = 0.3
    max_tokens: int = 4000
    timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0


class LLMClient:
    """
    Universal LLM client supporting multiple providers.

    Supports:
    - OpenAI (GPT-3.5, GPT-4, GPT-4-turbo)
    - Anthropic (Claude models)
    - Direct HTTP requests without wrapper libraries
    - Automatic retries and error handling
    - Token counting and cost estimation
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig(model="gpt-4")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CodeReviewAgent/1.0",
            "Content-Type": "application/json"
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds between requests

        # Cost tracking
        self.pricing = self._load_pricing()

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Generate text using the configured LLM.

        Args:
            prompt: The input prompt
            model: Override model (optional)
            temperature: Override temperature (optional)
            max_tokens: Override max tokens (optional)

        Returns:
            LLMResponse with generated content
        """
        start_time = time.time()

        # Use provided params or fall back to config
        model = model or self.config.model
        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        try:
            # Rate limiting
            self._rate_limit()

            # Route to appropriate provider
            if model.startswith("gpt") or model.startswith("text-davinci"):
                response = self._openai_generate(prompt, model, temperature, max_tokens)
            elif model.startswith("claude"):
                response = self._anthropic_generate(prompt, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported model: {model}")

            response.response_time = time.time() - start_time
            response.cost_estimate = self._estimate_cost(model, response.tokens_used or 0)

            return response

        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )

    def generate_with_retry(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate with automatic retry on failure."""
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                response = self.generate(prompt, model, **kwargs)
                if response.success:
                    return response
                last_error = response.error
            except Exception as e:
                last_error = str(e)

            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.retry_delay * (attempt + 1))

        return LLMResponse(
            content="",
            model=model or self.config.model,
            success=False,
            error=f"Failed after {self.config.max_retries} attempts. Last error: {last_error}"
        )

    def _openai_generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Determine if it's a chat model or completion model
        is_chat_model = model.startswith("gpt-3.5") or model.startswith("gpt-4")

        if is_chat_model:
            # Use Chat Completions API
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            url = "https://api.openai.com/v1/chat/completions"
        else:
            # Use legacy Completions API
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            url = "https://api.openai.com/v1/completions"

        response = self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        response.raise_for_status()
        data = response.json()

        # Handle different response formats
        if is_chat_model:
            content = data["choices"][0]["message"]["content"]
        else:
            content = data["choices"][0]["text"]

        tokens_used = data.get("usage", {}).get("total_tokens")

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens_used
        )

    def _anthropic_generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate using Anthropic API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        response.raise_for_status()
        data = response.json()

        content = data["content"][0]["text"]
        tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)

        return LLMResponse(
            content=content,
            model=model,
            tokens_used=tokens_used
        )

    def generate_structured_review(self, file_content: str, language: str, file_path: str) -> LLMResponse:
        """Generate a structured code review using a specialized prompt."""
        prompt = self._build_review_prompt(file_content, language, file_path)
        return self.generate(prompt)

    def generate_security_analysis(self, security_issues: List[Dict], file_path: str) -> LLMResponse:
        """Generate security analysis based on detected issues."""
        prompt = self._build_security_prompt(security_issues, file_path)
        return self.generate(prompt, temperature=0.1)  # Lower temperature for security analysis

    def generate_multi_file_review(self, file_analyses: List[Dict], context: str = "") -> LLMResponse:
        """Generate a comprehensive review for multiple files."""
        prompt = self._build_multi_file_prompt(file_analyses, context)
        return self.generate(prompt, max_tokens=6000)  # More tokens for multi-file reviews

    def _build_review_prompt(self, file_content: str, language: str, file_path: str) -> str:
        """Build a comprehensive code review prompt."""
        return f"""You are a senior software engineer performing a code review. Please analyze this {language} file and provide a comprehensive, constructive review.

File: {file_path}
Language: {language}

Code:
```{language.lower()}
{file_content}
```

Please provide a structured review with the following sections:

## Summary
Brief overview of what this code does (2-3 sentences).

## Quality Score
Rate the code quality from 1-10 with justification.

## Critical Issues
List any bugs, logic errors, or potential crashes with line numbers.

## Security Concerns
Identify any security vulnerabilities or risky patterns.

## Performance Issues
Point out any performance bottlenecks or inefficiencies.

## Best Practices
Evaluate adherence to {language} best practices and conventions.

## Maintainability
Assess code readability, documentation, and long-term maintainability.

## Suggestions
Specific recommendations for improvement with examples where helpful.

## Positive Aspects
Highlight well-written parts and good practices used.

## Overall Recommendation
Choose one: Approve / Request Changes / Needs Discussion

Focus on being constructive and educational. Provide specific line numbers when referencing issues."""

    def _build_security_prompt(self, security_issues: List[Dict], file_path: str) -> str:
        """Build a security-focused analysis prompt."""
        issues_text = "\n".join([
            f"- Line {issue.get('line_number', '?')}: {issue.get('message', 'Unknown issue')} (Severity: {issue.get('severity', 'unknown')})"
            for issue in security_issues
        ])

        return f"""You are a cybersecurity expert reviewing code for security vulnerabilities.

File: {file_path}

Security Issues Detected:
{issues_text}

Please provide:

## Security Risk Assessment
Overall risk level (Low/Medium/High/Critical) and justification.

## Detailed Analysis
For each issue, explain:
- The specific vulnerability
- How it could be exploited
- Potential impact
- Remediation steps

## Priority Recommendations
Order issues by severity and provide specific fix instructions.

## Security Best Practices
Additional security recommendations for this type of code.

Be specific about remediation steps and provide code examples where helpful."""

    def _build_multi_file_prompt(self, file_analyses: List[Dict], context: str) -> str:
        """Build a prompt for reviewing multiple related files."""
        files_summary = "\n".join([
            f"File: {analysis.get('file_path', 'Unknown')}\n"
            f"Language: {analysis.get('language', 'Unknown')}\n"
            f"Issues: {len(analysis.get('issues', []))}\n"
            f"Summary: {analysis.get('summary', 'No summary available')}\n"
            for analysis in file_analyses
        ])

        return f"""You are reviewing multiple related code files as a cohesive system.

Context: {context}

Files in Review:
{files_summary}

Please provide:

## System Overview
How these files work together and their overall purpose.

## Architecture Assessment
Evaluate the overall design and file organization.

## Cross-File Issues
Identify problems that span multiple files:
- Inconsistent patterns
- Circular dependencies
- Duplicated logic
- Interface mismatches

## Integration Concerns
Potential issues when these components work together.

## Consistency Analysis
Evaluate coding style and pattern consistency across files.

## Overall Quality Score
Rate the entire system (1-10) with justification.

## System-Level Recommendations
Suggest improvements for the overall architecture and organization.

## Priority Action Items
List the most important changes needed across the system.

Focus on how these files interact and the overall system design."""

    def _rate_limit(self):
        """Implement simple rate limiting."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def _load_pricing(self) -> Dict[str, Dict[str, float]]:
        """Load pricing information for cost estimation."""
        return {
            # OpenAI pricing (per 1K tokens) - approximate values
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            # Anthropic pricing (per 1K tokens) - approximate values
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
        }

    def _estimate_cost(self, model: str, tokens_used: int) -> Optional[float]:
        """Estimate the cost of the API call."""
        if model not in self.pricing or not tokens_used:
            return None

        # Simple estimation (assumes equal input/output split)
        model_pricing = self.pricing[model]
        avg_price = (model_pricing["input"] + model_pricing["output"]) / 2
        return (tokens_used / 1000) * avg_price

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return [
            # OpenAI models
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-0125-preview",
            # Anthropic models
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229",
        ]

    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that API keys are configured."""
        return {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY"))
        }

    def test_connection(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Test the connection to the LLM API."""
        test_model = model or self.config.model

        try:
            response = self.generate(
                "Hello, this is a test. Please respond with 'Connection successful.'",
                model=test_model,
                max_tokens=50
            )

            return {
                "success": response.success,
                "model": test_model,
                "response_time": response.response_time,
                "error": response.error
            }
        except Exception as e:
            return {
                "success": False,
                "model": test_model,
                "error": str(e)
            }


# Convenience functions for quick usage
def quick_review(file_content: str, language: str, model: str = "gpt-4") -> str:
    """Quick file review using default settings."""
    client = LLMClient(LLMConfig(model=model))
    response = client.generate_structured_review(file_content, language, "file")
    return response.content if response.success else f"Error: {response.error}"


def quick_security_check(security_issues: List[Dict], model: str = "gpt-4") -> str:
    """Quick security analysis using default settings."""
    client = LLMClient(LLMConfig(model=model))
    response = client.generate_security_analysis(security_issues, "file")
    return response.content if response.success else f"Error: {response.error}"


# Model aliases for convenience
class Models:
    """Common model aliases."""
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_OPUS = "claude-3-opus-20240229"