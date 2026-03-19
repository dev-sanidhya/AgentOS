"""
Research Agent Tools Package

This package contains modular tools for the Raw Python research agent:
- web_search: Direct API calls to search services
- web_scrape: BeautifulSoup web scraping functionality
- llm_client: Direct LLM API client for OpenAI and Anthropic

Each tool is designed to be independent and reusable.
"""

from .web_search import WebSearchClient
from .web_scrape import WebScraperClient
from .llm_client import LLMClient

__all__ = [
    'WebSearchClient',
    'WebScraperClient',
    'LLMClient'
]

__version__ = "1.0.0"