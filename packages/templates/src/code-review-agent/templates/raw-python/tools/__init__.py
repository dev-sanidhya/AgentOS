"""
Code Review Agent Tools

This package contains modular tools for comprehensive code review:

- file_analyzer: File analysis and metrics calculation
- security_scanner: Security vulnerability detection
- llm_client: Direct LLM API client for OpenAI and Anthropic

Each tool can be used independently or together for comprehensive code review.
"""

from .file_analyzer import FileAnalyzer, FileMetrics, CodeIssue
from .security_scanner import SecurityScanner, SecurityIssue, SecurityReport
from .llm_client import LLMClient, LLMConfig, LLMResponse, Models

__all__ = [
    # File Analysis
    'FileAnalyzer',
    'FileMetrics',
    'CodeIssue',

    # Security Scanning
    'SecurityScanner',
    'SecurityIssue',
    'SecurityReport',

    # LLM Client
    'LLMClient',
    'LLMConfig',
    'LLMResponse',
    'Models',
]

__version__ = "1.0.0"