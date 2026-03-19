"""
Web Search Tool

Searches the web for information using a search API.

To use with real search:
1. Sign up for a search API (Brave Search, SerpAPI, or Tavily)
2. Add your API key to .env
3. Uncomment the appropriate implementation below
"""

from langchain.tools import Tool
from typing import List, Dict
import os


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web for information.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of search results with title, url, and snippet
    """

    # ================================================
    # OPTION 1: Brave Search API (Recommended)
    # ================================================
    # Uncomment to use Brave Search:
    #
    # import requests
    # api_key = os.getenv("BRAVE_API_KEY")
    # url = "https://api.search.brave.com/res/v1/web/search"
    # headers = {"X-Subscription-Token": api_key}
    # params = {"q": query, "count": max_results}
    #
    # response = requests.get(url, headers=headers, params=params)
    # data = response.json()
    #
    # results = []
    # for item in data.get("web", {}).get("results", []):
    #     results.append({
    #         "title": item.get("title", ""),
    #         "url": item.get("url", ""),
    #         "snippet": item.get("description", "")
    #     })
    # return results

    # ================================================
    # OPTION 2: SerpAPI (Google Search)
    # ================================================
    # Uncomment to use SerpAPI:
    #
    # from serpapi import GoogleSearch
    # api_key = os.getenv("SERPAPI_KEY")
    # params = {
    #     "q": query,
    #     "api_key": api_key,
    #     "num": max_results
    # }
    #
    # search = GoogleSearch(params)
    # data = search.get_dict()
    #
    # results = []
    # for item in data.get("organic_results", []):
    #     results.append({
    #         "title": item.get("title", ""),
    #         "url": item.get("link", ""),
    #         "snippet": item.get("snippet", "")
    #     })
    # return results

    # ================================================
    # OPTION 3: Tavily Search (AI-optimized)
    # ================================================
    # Uncomment to use Tavily:
    #
    # from tavily import TavilyClient
    # api_key = os.getenv("TAVILY_API_KEY")
    # client = TavilyClient(api_key=api_key)
    #
    # response = client.search(query, max_results=max_results)
    #
    # results = []
    # for item in response.get("results", []):
    #     results.append({
    #         "title": item.get("title", ""),
    #         "url": item.get("url", ""),
    #         "snippet": item.get("content", "")
    #     })
    # return results

    # ================================================
    # PLACEHOLDER (for testing without API)
    # ================================================
    print(f"[MOCK] Searching for: {query}")
    return [
        {
            "title": f"Search result for: {query}",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
            "snippet": f"This is a mock search result for '{query}'. "
                      f"Set up a real search API to get actual results. "
                      f"See web_search.py for integration options."
        }
    ]


# Create LangChain tool
web_search_tool = Tool(
    name="web_search",
    description=(
        "Search the web for information on any topic. "
        "Useful for finding current information, facts, news, and articles. "
        "Input should be a clear, specific search query. "
        "Returns a list of relevant web pages with titles and snippets."
    ),
    func=lambda query: web_search(query, max_results=5)
)
