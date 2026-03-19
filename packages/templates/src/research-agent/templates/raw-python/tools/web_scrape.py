"""
Web Scraper Client for Research Agent

BeautifulSoup-based web scraping with intelligent content extraction.
Handles various content types and provides clean, readable text extraction.
"""

import os
import re
import requests
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

try:
    from bs4 import BeautifulSoup, Comment
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


@dataclass
class ScrapedContent:
    """Represents scraped content from a web page."""
    url: str
    title: Optional[str]
    text: str
    word_count: int
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class WebScraperClient:
    """
    Web scraper client using BeautifulSoup for intelligent content extraction.

    Features:
    - Intelligent content extraction
    - HTML cleaning and text normalization
    - Multiple fallback methods
    - Metadata extraction
    - Error handling and rate limiting
    """

    def __init__(
        self,
        timeout: int = 15,
        max_content_length: int = 10000,
        user_agent: str = None
    ):
        """
        Initialize web scraper client.

        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to extract
            user_agent: Custom User-Agent header
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Common headers for web requests
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape content from a URL.

        Args:
            url: URL to scrape

        Returns:
            ScrapedContent object with extracted text and metadata
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return ScrapedContent(
                    url=url,
                    title=None,
                    text="",
                    word_count=0,
                    success=False,
                    error="Invalid URL format"
                )

            # Make request
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'html' not in content_type:
                return ScrapedContent(
                    url=url,
                    title=None,
                    text=f"Non-HTML content type: {content_type}",
                    word_count=0,
                    success=False,
                    error=f"Unsupported content type: {content_type}"
                )

            # Parse with BeautifulSoup if available
            if BEAUTIFULSOUP_AVAILABLE:
                return self._scrape_with_beautifulsoup(url, response.text)
            else:
                return self._scrape_with_regex(url, response.text)

        except requests.exceptions.Timeout:
            return ScrapedContent(
                url=url,
                title=None,
                text="",
                word_count=0,
                success=False,
                error="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            return ScrapedContent(
                url=url,
                title=None,
                text="",
                word_count=0,
                success=False,
                error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            return ScrapedContent(
                url=url,
                title=None,
                text="",
                word_count=0,
                success=False,
                error=f"Scraping failed: {str(e)}"
            )

    def _scrape_with_beautifulsoup(self, url: str, html: str) -> ScrapedContent:
        """
        Scrape content using BeautifulSoup for intelligent extraction.

        Args:
            url: Original URL
            html: HTML content

        Returns:
            ScrapedContent object
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract title
            title = self._extract_title(soup)

            # Remove unwanted elements
            self._clean_soup(soup)

            # Extract main content
            text = self._extract_main_content(soup)

            # Clean and normalize text
            text = self._clean_text(text)

            # Limit content length
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."

            # Extract metadata
            metadata = self._extract_metadata(soup)

            word_count = len(text.split())

            return ScrapedContent(
                url=url,
                title=title,
                text=text,
                word_count=word_count,
                success=True,
                metadata=metadata
            )

        except Exception as e:
            return self._scrape_with_regex(url, html)

    def _scrape_with_regex(self, url: str, html: str) -> ScrapedContent:
        """
        Fallback scraping using regex (when BeautifulSoup is not available).

        Args:
            url: Original URL
            html: HTML content

        Returns:
            ScrapedContent object
        """
        try:
            # Extract title using regex
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else None

            # Remove script and style tags
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)

            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)

            # Clean text
            text = self._clean_text(text)

            # Limit content length
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."

            word_count = len(text.split())

            return ScrapedContent(
                url=url,
                title=title,
                text=text,
                word_count=word_count,
                success=True,
                metadata={"extraction_method": "regex"}
            )

        except Exception as e:
            return ScrapedContent(
                url=url,
                title=None,
                text="",
                word_count=0,
                success=False,
                error=f"Regex extraction failed: {str(e)}"
            )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title from soup."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        # Try og:title
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()

        # Try h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()

        return None

    def _clean_soup(self, soup: BeautifulSoup) -> None:
        """Remove unwanted elements from soup."""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe", "object", "embed"]):
            script.decompose()

        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove navigation, sidebar, footer elements
        for element in soup(["nav", "aside", "footer", "header"]):
            element.decompose()

        # Remove elements by class/id (common patterns)
        unwanted_patterns = [
            'sidebar', 'navigation', 'nav', 'menu', 'footer', 'header',
            'advertisement', 'ads', 'social', 'share', 'comment'
        ]

        for pattern in unwanted_patterns:
            for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                element.decompose()
            for element in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
                element.decompose()

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from cleaned soup."""
        # Try to find main content areas first
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '.article-content',
            '.post-content',
            '#content',
            '#main-content'
        ]

        for selector in content_selectors:
            content = soup.select(selector)
            if content:
                return '\n\n'.join(element.get_text() for element in content)

        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text()

        # Last resort - all text
        return soup.get_text()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove HTML entities
        import html
        text = html.unescape(text)

        return text

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the page."""
        metadata = {
            "extraction_method": "beautifulsoup"
        }

        # Description
        description_meta = soup.find('meta', attrs={'name': 'description'})
        if description_meta:
            metadata['description'] = description_meta.get('content', '')

        # Open Graph data
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                metadata[f'og_{property_name}'] = content

        # Keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            metadata['keywords'] = keywords_meta.get('content', '')

        # Author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            metadata['author'] = author_meta.get('content', '')

        return metadata

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def bulk_scrape(self, urls: List[str]) -> List[ScrapedContent]:
        """
        Scrape multiple URLs.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of ScrapedContent objects
        """
        results = []
        for url in urls:
            result = self.scrape(url)
            results.append(result)

        return results

    def get_text_summary(self, content: ScrapedContent, max_words: int = 100) -> str:
        """
        Get a summary of scraped content.

        Args:
            content: ScrapedContent object
            max_words: Maximum words in summary

        Returns:
            Text summary
        """
        if not content.success:
            return f"Failed to scrape: {content.error}"

        words = content.text.split()
        if len(words) <= max_words:
            return content.text

        summary_words = words[:max_words]
        return ' '.join(summary_words) + '...'