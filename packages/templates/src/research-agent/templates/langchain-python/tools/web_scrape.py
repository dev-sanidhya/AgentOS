"""
Web Scraping Tool

Fetches and extracts text content from web pages.
"""

from langchain.tools import Tool
from typing import Dict
import requests
from bs4 import BeautifulSoup


def web_scrape(url: str, selector: str = None) -> Dict[str, str]:
    """
    Scrape content from a web page.

    Args:
        url: URL to scrape
        selector: Optional CSS selector for specific content

    Returns:
        Dictionary with url, content, title, and length
    """
    try:
        # Fetch the page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract content
        if selector:
            # Use CSS selector if provided
            elements = soup.select(selector)
            content = ' '.join([el.get_text() for el in elements])
        else:
            # Extract main content
            content = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)

        # Limit content length
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        # Extract title
        title = soup.find('title')
        title_text = title.string if title else "No title"

        return {
            "url": url,
            "title": title_text,
            "content": content,
            "length": len(content)
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "error": f"Failed to fetch {url}: {str(e)}",
            "content": "",
            "length": 0
        }
    except Exception as e:
        return {
            "url": url,
            "error": f"Failed to parse {url}: {str(e)}",
            "content": "",
            "length": 0
        }


def _web_scrape_wrapper(url: str) -> str:
    """Wrapper function for LangChain tool."""
    result = web_scrape(url)

    if "error" in result:
        return f"Error: {result['error']}"

    return f"Title: {result['title']}\n\nContent:\n{result['content']}"


# Create LangChain tool
web_scrape_tool = Tool(
    name="web_scrape",
    description=(
        "Extract text content from a web page given its URL. "
        "Useful for reading articles, blog posts, and web pages in detail. "
        "Input should be a valid URL (starting with http:// or https://). "
        "Returns the page title and main text content."
    ),
    func=_web_scrape_wrapper
)
