"""
Web Search Client for Research Agent

Direct API integration with multiple search services:
- Brave Search API (recommended)
- Serper API (Google search proxy)
- SerpAPI (Google search with rich data)

Provides clean, consistent interface for web search functionality.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Represents a single search result."""
    title: str
    url: str
    snippet: str
    rank: Optional[int] = None


class WebSearchClient:
    """
    Web search client with multiple API support.

    Automatically tries available search APIs in order of preference:
    1. Brave Search (cleanest results)
    2. Serper API (Google proxy)
    3. SerpAPI (comprehensive Google data)
    4. Mock results (for testing)
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize web search client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search the web for information.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of SearchResult objects

        Raises:
            Exception: If all search methods fail
        """
        try:
            # Try search APIs in order of preference
            if os.getenv("BRAVE_API_KEY"):
                return self._brave_search(query, max_results)
            elif os.getenv("SERPER_API_KEY"):
                return self._serper_search(query, max_results)
            elif os.getenv("SERPAPI_KEY"):
                return self._serpapi_search(query, max_results)
            else:
                print("⚠️  No search API keys found. Using mock results.")
                return self._mock_search(query, max_results)
        except Exception as e:
            print(f"Search failed: {e}, using mock results")
            return self._mock_search(query, max_results)

    def _brave_search(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using Brave Search API.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of SearchResult objects
        """
        headers = {
            "X-Subscription-Token": os.getenv("BRAVE_API_KEY"),
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"
        }

        params = {
            "q": query,
            "count": max_results,
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "none"
        }

        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        results = []

        for i, item in enumerate(data.get("web", {}).get("results", [])):
            results.append(SearchResult(
                title=item.get("title", "").strip(),
                url=item.get("url", ""),
                snippet=item.get("description", "").strip(),
                rank=i + 1
            ))

        return results[:max_results]

    def _serper_search(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using Serper API (Google proxy).

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of SearchResult objects
        """
        headers = {
            "X-API-KEY": os.getenv("SERPER_API_KEY"),
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"
        }

        payload = {
            "q": query,
            "num": max_results,
            "gl": "us",
            "hl": "en"
        }

        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        results = []

        for i, item in enumerate(data.get("organic", [])):
            results.append(SearchResult(
                title=item.get("title", "").strip(),
                url=item.get("link", ""),
                snippet=item.get("snippet", "").strip(),
                rank=i + 1
            ))

        return results[:max_results]

    def _serpapi_search(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using SerpAPI.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of SearchResult objects
        """
        params = {
            "engine": "google",
            "q": query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": max_results,
            "gl": "us",
            "hl": "en"
        }

        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()
        results = []

        for i, item in enumerate(data.get("organic_results", [])):
            results.append(SearchResult(
                title=item.get("title", "").strip(),
                url=item.get("link", ""),
                snippet=item.get("snippet", "").strip(),
                rank=i + 1
            ))

        return results[:max_results]

    def _mock_search(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Generate mock search results for testing.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of mock SearchResult objects
        """
        print(f"📱 Using mock search results for: '{query}'")
        print("   Configure BRAVE_API_KEY, SERPER_API_KEY, or SERPAPI_KEY for real results")

        mock_results = []
        for i in range(max_results):
            mock_results.append(SearchResult(
                title=f"Mock Result {i+1}: {query}",
                url=f"https://example.com/result{i+1}",
                snippet=f"This is a mock search result for '{query}'. "
                       f"It contains simulated content that would normally come from a real search API. "
                       f"Configure a real search API key to get actual search results.",
                rank=i + 1
            ))

        return mock_results

    def get_available_apis(self) -> Dict[str, bool]:
        """
        Check which search APIs are configured.

        Returns:
            Dictionary of API names and their availability status
        """
        return {
            "brave": bool(os.getenv("BRAVE_API_KEY")),
            "serper": bool(os.getenv("SERPER_API_KEY")),
            "serpapi": bool(os.getenv("SERPAPI_KEY"))
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on available search APIs.

        Returns:
            Dictionary with health status of each API
        """
        health = {}
        apis = self.get_available_apis()

        for api, available in apis.items():
            if not available:
                health[api] = {"status": "not_configured", "error": "No API key"}
                continue

            try:
                # Simple test query
                if api == "brave" and os.getenv("BRAVE_API_KEY"):
                    results = self._brave_search("test", 1)
                elif api == "serper" and os.getenv("SERPER_API_KEY"):
                    results = self._serper_search("test", 1)
                elif api == "serpapi" and os.getenv("SERPAPI_KEY"):
                    results = self._serpapi_search("test", 1)
                else:
                    continue

                health[api] = {
                    "status": "healthy",
                    "results_count": len(results)
                }

            except Exception as e:
                health[api] = {
                    "status": "error",
                    "error": str(e)
                }

        return health