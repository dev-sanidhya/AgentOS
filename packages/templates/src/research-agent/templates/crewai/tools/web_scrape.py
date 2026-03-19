"""
Web Scraping Tool for CrewAI Integration

This tool extracts and processes content from web pages,
with smart content detection and cleaning capabilities.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional
from crewai_tools import BaseTool


class WebScrapeTool(BaseTool):
    name: str = "web_scrape"
    description: str = """
    Extract and analyze content from any web page.
    Input: URL of the webpage to scrape
    Output: Cleaned text content from the webpage
    """

    def _run(self, url: str, selector: Optional[str] = None) -> str:
        """
        Scrape content from the given URL.

        Args:
            url: The webpage URL to scrape
            selector: Optional CSS selector to target specific content

        Returns:
            Extracted and cleaned text content
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return f"Invalid URL: {url}"

            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Cache-Control': 'no-cache',
                'Upgrade-Insecure-Requests': '1'
            }

            # Make request with timeout
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract content based on selector or smart content detection
            if selector:
                content = self._extract_by_selector(soup, selector, url)
            else:
                content = self._smart_content_extraction(soup)

            # Clean and format the content
            cleaned_content = self._clean_text(content)

            if not cleaned_content or len(cleaned_content) < 50:
                return f"Unable to extract meaningful content from {url}. The page might be JavaScript-heavy or access-restricted."

            # Limit content length to avoid token overflow
            max_length = 5000
            if len(cleaned_content) > max_length:
                cleaned_content = cleaned_content[:max_length] + "\n\n[Content truncated for length...]"

            return f"Content extracted from {url}:\n\n{cleaned_content}"

        except requests.exceptions.RequestException as e:
            return f"Failed to fetch {url}: {str(e)}"
        except Exception as e:
            return f"Error processing {url}: {str(e)}"

    def _extract_by_selector(self, soup: BeautifulSoup, selector: str, url: str) -> str:
        """Extract content using CSS selector."""
        elements = soup.select(selector)

        if not elements:
            return f"No content found with selector '{selector}' on {url}"

        # Extract text from all matching elements
        content_parts = []
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short content
                content_parts.append(text)

        return '\n\n'.join(content_parts)

    def _smart_content_extraction(self, soup: BeautifulSoup) -> str:
        """Intelligently extract main content from webpage."""

        # Remove unwanted elements
        for element in soup.find_all([
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'iframe', 'noscript', 'form'
        ]):
            element.decompose()

        # Remove elements with common non-content classes/ids
        unwanted_selectors = [
            '[class*="ad"]', '[class*="advertisement"]', '[class*="sidebar"]',
            '[class*="menu"]', '[class*="navigation"]', '[class*="banner"]',
            '[class*="popup"]', '[class*="modal"]', '[class*="overlay"]',
            '[id*="ad"]', '[id*="sidebar"]', '[id*="menu"]'
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Try to find main content using common patterns
        content_selectors = [
            'main', 'article', '[role="main"]', '.main-content',
            '.content', '#content', '.post', '.article', '.entry',
            '.text', '.body'
        ]

        content_element = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 200:
                content_element = element
                break

        # Fallback to body if no specific content area found
        if not content_element:
            content_element = soup.find('body')

        if not content_element:
            return soup.get_text(strip=True)

        # Extract text with some basic structure preservation
        return self._extract_structured_text(content_element)

    def _extract_structured_text(self, element) -> str:
        """Extract text while preserving some structure."""
        text_parts = []

        for child in element.descendants:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = child.get_text(strip=True)
                if text:
                    text_parts.append(f"\n## {text}\n")
            elif child.name in ['p', 'div']:
                text = child.get_text(strip=True)
                if text and len(text) > 30:  # Filter short paragraphs
                    text_parts.append(text)
            elif child.name == 'li':
                text = child.get_text(strip=True)
                if text:
                    text_parts.append(f"• {text}")

        # If structured extraction doesn't yield much, fall back to simple text
        structured_text = '\n'.join(text_parts)
        if len(structured_text) < 200:
            return element.get_text(strip=True)

        return structured_text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""

        # Normalize whitespace
        import re

        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)

        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Clean up lines
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip very short lines (likely navigation elements)
            if len(line) > 10:
                cleaned_lines.append(line)

        # Join lines and final cleanup
        cleaned_text = '\n'.join(cleaned_lines).strip()

        # Remove excessive repetition
        cleaned_text = re.sub(r'(\n.*?){10,}(\n\1)+', r'\1', cleaned_text)

        return cleaned_text