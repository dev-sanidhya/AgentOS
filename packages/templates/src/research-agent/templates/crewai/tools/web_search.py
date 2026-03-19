"""
Web Search Tool for CrewAI Integration

This tool provides web search capabilities using various search APIs,
with fallback to mock search for development and testing.
"""

import os
import requests
from typing import Optional, List, Dict, Any
from crewai_tools import BaseTool


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = """
    Search the web for information on any topic.
    Input: Search query (string)
    Output: Search results with titles, URLs, and descriptions
    """

    def _run(self, query: str, max_results: int = 5) -> str:
        """Execute web search with the given query."""
        try:
            # Try different search APIs in order of preference
            if os.getenv("BRAVE_API_KEY"):
                return self._search_with_brave(query, max_results)
            elif os.getenv("SERPAPI_KEY"):
                return self._search_with_serpapi(query, max_results)
            elif os.getenv("TAVILY_API_KEY"):
                return self._search_with_tavily(query, max_results)
            else:
                return self._mock_search(query, max_results)
        except Exception as e:
            print(f"Search error: {e}")
            return self._mock_search(query, max_results)

    def _search_with_brave(self, query: str, max_results: int) -> str:
        """Search using Brave Search API."""
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': os.getenv('BRAVE_API_KEY')
        }

        params = {
            'q': query,
            'count': max_results,
            'search_lang': 'en',
            'country': 'US',
            'safesearch': 'moderate'
        }

        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Brave API error: {response.status_code}")

        data = response.json()
        results = data.get('web', {}).get('results', [])

        if not results:
            return f"No results found for '{query}' using Brave Search."

        formatted_results = []
        for i, result in enumerate(results[:max_results], 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', 'No URL')}\n"
                f"   {result.get('description', 'No description')}"
            )

        return f"Search results for '{query}':\n\n" + '\n\n'.join(formatted_results)

    def _search_with_serpapi(self, query: str, max_results: int) -> str:
        """Search using SerpAPI (Google Search)."""
        params = {
            'engine': 'google',
            'q': query,
            'num': max_results,
            'api_key': os.getenv('SERPAPI_KEY')
        }

        response = requests.get(
            'https://serpapi.com/search.json',
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"SerpAPI error: {response.status_code}")

        data = response.json()
        results = data.get('organic_results', [])

        if not results:
            return f"No results found for '{query}' using Google Search."

        formatted_results = []
        for i, result in enumerate(results[:max_results], 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('link', 'No URL')}\n"
                f"   {result.get('snippet', 'No description')}"
            )

        return f"Google search results for '{query}':\n\n" + '\n\n'.join(formatted_results)

    def _search_with_tavily(self, query: str, max_results: int) -> str:
        """Search using Tavily AI Search API."""
        payload = {
            'api_key': os.getenv('TAVILY_API_KEY'),
            'query': query,
            'search_depth': 'advanced',
            'include_answer': True,
            'include_images': False,
            'include_raw_content': False,
            'max_results': max_results
        }

        response = requests.post(
            'https://api.tavily.com/search',
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Tavily API error: {response.status_code}")

        data = response.json()
        results = data.get('results', [])

        if not results:
            return f"No results found for '{query}' using Tavily Search."

        formatted_results = []
        for i, result in enumerate(results[:max_results], 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', 'No URL')}\n"
                f"   {result.get('content', 'No content')}"
            )

        search_result = f"AI-enhanced search results for '{query}':\n\n" + '\n\n'.join(formatted_results)

        # Add AI summary if available
        if data.get('answer'):
            search_result = f"AI Summary: {data['answer']}\n\n{search_result}"

        return search_result

    def _mock_search(self, query: str, max_results: int) -> str:
        """Provide mock search results for development/testing."""
        print("⚠️  Using mock search results. Set up a search API for real results.")

        mock_results = [
            {
                'title': f"Mock Result 1 for '{query}'",
                'url': 'https://example.com/result1',
                'description': 'This is a placeholder search result. Configure a real search API (Brave, SerpAPI, or Tavily) for actual web search.'
            },
            {
                'title': f"Mock Result 2 for '{query}'",
                'url': 'https://example.com/result2',
                'description': 'Another mock result showing what real search would return with proper API configuration.'
            },
            {
                'title': f"Mock Result 3 for '{query}'",
                'url': 'https://example.com/result3',
                'description': 'Configure BRAVE_API_KEY, SERPAPI_KEY, or TAVILY_API_KEY in your environment to enable real search.'
            }
        ]

        formatted_results = []
        for i, result in enumerate(mock_results[:max_results], 1):
            formatted_results.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['url']}\n"
                f"   {result['description']}"
            )

        return (
            f"🔍 Mock search results for '{query}':\n\n"
            + '\n\n'.join(formatted_results)
            + "\n\n💡 Set up a search API (Brave, SerpAPI, or Tavily) for real results."
        )